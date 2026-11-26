import {el} from '../dom.js';
import {mill} from '../mill-api.js';
import {desk, movements, ticketStates} from '../mill-state.js';
import {actionForm, input, kilograms, mayWrite} from '../weights.js';
import {dataView, status, titleBlock} from '../widgets.js';
import {pill} from '../components/state-pill.js';

export async function scale(root, role) {
  const rail = el('div',{class:'cardrail'});
  const details = el('div',{class:'ticket-detail'});
  const changeList = el('div',{});
  let selected = desk.activeTicket;
  async function loadLedger() {
    const rows = (await mill.movements()).map(row => ({...row, action:movements[row.action], weight:kilograms(row.grams)}));
    changeList.replaceChildren(dataView(rows,[{name:'ticket_code',label:'称量单'},{name:'lot_code',label:'批号'},
      {name:'action',label:'事件'},{name:'weight',label:'重量'}],'table'));
  }
  async function open(code) {
    selected = desk.activeTicket = code;
    for (const button of rail.querySelectorAll('button')) button.setAttribute('aria-pressed',String(button.textContent === code));
    const data = await mill.ticket(code);
    const job = data.ticket;
    const closed = ['released','cancelled'].includes(job.state);
    const list = el('div',{class:'weigh-list'});
    const controls = el('div',{});
    details.replaceChildren(el('h2',{class:'mono'},job.code), pill(ticketStates[job.state],job.state),
      el('p',{},job.zone_code + ' · 总重 ' + kilograms(job.total_g) + ' · CLR ' + job.clearance.toFixed(4)),list,controls);
    for (const line of data.lines) {
      const row = el('div',{class:'scale-row','data-actual':String(line.actual_g !== null)},
        el('h3',{},line.lot_code || '新料'),el('p',{class:'mono'},'应称 ' + kilograms(line.required_g) +
          (line.actual_g === null ? '' : ' · 已记录 ' + kilograms(line.actual_g))));
      if (!closed && mayWrite(role) && line.actual_g === null) {
        row.append(actionForm('read-' + line.code,[input('grams','秤读数（g）',{type:'number',min:'50',step:'50'})],
          '写入秤读',async fields => {
            await mill.read(job.code,{line_code:line.code,grams:Number(fields.get('grams'))});
            await open(job.code);
          }));
      }
      list.append(row);
    }
    if (job.state === 'released') controls.append(el('a',{href:'#patch'},'前往补坪验收'));
    if (!closed && role === 'reviewer') {
      if (job.state === 'weighed') controls.append(actionForm('release',[],'签发料单',async () => {
        await mill.finalize(code,'release');
        await Promise.all([open(code),loadLedger()]);
      }));
      controls.append(actionForm('cancel',[],'退订并解锁',async () => {
        await mill.finalize(code,'cancel');
        await Promise.all([open(code),loadLedger()]);
      }));
    }
  }
  const tickets = await mill.tickets();
  rail.replaceChildren(...tickets.map(item => el('button',{type:'button',class:'quiet',
    onclick:() => open(item.code).catch(error=>details.replaceChildren(status(error.message,'error')))},item.code)));
  root.replaceChildren(titleBlock('现场 · 道口秤', '逐行称量与发料', '每个来源单独记录秤读。复核员签发后，回收料余量和扣减履历同时更新。'),
    el('div',{class:'workspace-split'},el('section',{class:'ledger'},rail,details),
      el('section',{class:'ledger'},el('h2',{},'锁料与扣减流水'),changeList)));
  if (tickets.length) await open(tickets.some(item=>item.code===selected) ? selected : tickets[0].code);
  else details.replaceChildren(status('暂无称量单。完成配方计算后即可锁料开单。'));
  await loadLedger();
}
