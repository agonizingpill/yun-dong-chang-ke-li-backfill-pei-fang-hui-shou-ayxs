from fastapi import HTTPException
from core.audit import record
from core.db import transaction
from domain.blend_tables import lines, tickets
from domain.catalog import lookup, ticket_lines
from domain.intake_tables import lots
from domain.movements import post
from domain.rules import TicketState


def closed_error():
    raise HTTPException(409, "已发料或已退订称量单不能再次办理")


def weigh(ticket_code, form, user):
    with transaction() as conn:
        ticket = lookup(conn, tickets, ticket_code, lock=True)
        if ticket["state"] not in (TicketState.RESERVED, TicketState.WEIGHED):
            closed_error()
        line = lookup(conn, lines, form.line_code)
        if line["ticket_code"] != ticket_code:
            raise HTTPException(409, "称量行属于另一张单")
        if form.grams != line["required_g"]:
            raise HTTPException(409, f"秤读数须与建议 {line['required_g']} g 一致，补料或移除后重扫")
        conn.execute(lines.update().where(lines.c.code == form.line_code).values(actual_g=form.grams))
        complete = all(row["actual_g"] is not None for row in ticket_lines(conn, ticket_code))
        new_state = TicketState.WEIGHED if complete else TicketState.RESERVED
        conn.execute(tickets.update().where(tickets.c.code == ticket_code).values(state=new_state))
        record(conn, user, f"weigh:{form.line_code}:{form.grams}")
        return {"code": ticket_code, "state": new_state, "line": form.line_code}


def finalize(ticket_code, user, *, cancel=False):
    next_state, movement = (TicketState.CANCELLED, "return") if cancel else (TicketState.RELEASED, "consume")
    with transaction() as conn:
        item = lookup(conn, tickets, ticket_code, lock=True)
        if item["state"] in (TicketState.RELEASED, TicketState.CANCELLED):
            closed_error()
        if not cancel and item["state"] != TicketState.WEIGHED:
            raise HTTPException(409, "每一行都完成秤读校验后才能发料")
        weighed = sorted(ticket_lines(conn, ticket_code), key=lambda line: line["lot_code"] or "")
        for line in weighed:
            code = line["lot_code"]
            if not code:
                continue
            lot = lookup(conn, lots, code, lock=True)
            amount = line["required_g"]
            conn.execute(lots.update().where(lots.c.code == code).values(
                reserved_g=lot["reserved_g"] - amount,
                available_g=lot["available_g"] - (0 if cancel else line["actual_g"])))
            post(conn, code, ticket_code, movement, amount, user)
        conn.execute(tickets.update().where(tickets.c.code == ticket_code)
                     .values(state=next_state, finalized_by=user["sub"]))
        record(conn, user, f"{movement}:{ticket_code}")
    return {"code": ticket_code, "state": next_state}
