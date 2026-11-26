from math import log, sqrt
from domain.rules import BINS, GRAM_STEP, ZeroMode

DETECTION_GRAMS = 0.5


def close(values):
    total = sum(values)
    if total <= 0:
        raise ValueError("无法对空组成闭合")
    return [value / total for value in values]


def restore_minor(values, zero_mode):
    zeros = values.count(0)
    if not zeros:
        return close(values), 0
    if zero_mode != ZeroMode.BELOW_LIMIT:
        raise ValueError("真实缺档不能用检测下限补齐")
    mass = sum(values)
    # Half the 1 g detection limit with proportional shrinkage of observed parts.
    scale = (mass - DETECTION_GRAMS * zeros) / mass
    return close([value * scale if value else DETECTION_GRAMS for value in values]), zeros


def clr(parts):
    if any(value <= 0 for value in parts):
        raise ValueError("中心化对数比要求所有档位严格正值")
    logs = [log(value) for value in parts]
    center = sum(logs) / len(logs)
    return [value - center for value in logs]


def distance(left, right):
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def fitted_parts(amounts, shares, total_g):
    return [sum(grams * share[index] for grams, share in zip(amounts, shares, strict=True))
            / total_g for index in range(len(BINS))]


def choose_amounts(total_g, limits, target_clr, shares, max_reclaimed, max_clearance):
    # Each candidate represents a physically measurable 50 g scale setting.
    possible = sorted(limits.items())
    cap = min(max_reclaimed, sum(limit for _, limit in possible)) // GRAM_STEP * GRAM_STEP
    for reclaim in range(cap, GRAM_STEP - 1, -GRAM_STEP):
        if len(possible) == 1:
            candidates = [[reclaim]]
        else:
            upper = min(reclaim, possible[0][1]) // GRAM_STEP * GRAM_STEP
            lower = max(0, reclaim - possible[1][1])
            candidates = ([first, reclaim - first] for first in range(upper, lower - 1, -GRAM_STEP))
        best = None
        for reclaimed in candidates:
            weights = [*reclaimed, total_g - reclaim]
            blend = clr(fitted_parts(weights, shares, total_g))
            score = distance(target_clr, blend)
            if score <= max_clearance and (best is None or (score, weights) < best[:2]):
                best = (score, weights, blend)
        if best:
            return best
    raise ValueError("没有满足该区 CLR 容差的 50 g 处置配方，请更换可用回收批")


def calculate(payload):
    zone, restored = payload["zone"], []
    target = clr(close([zone[name + "_pt"] for name in BINS]))
    fresh = close([zone["new_" + name + "_pt"] for name in BINS])
    records = sorted(payload["batches"], key=lambda item: item["code"])
    weights = {}
    for item in records:
        part, zero_count = restore_minor(item["sieve"], item["zero_mode"])
        restored.append({"code": item["code"], "parts": part, "clr": clr(part),
                         "zero_replacements": zero_count})
        weights[item["code"]] = item["free_g"]
    total = payload["total_g"]
    score, amounts, blend = choose_amounts(total, weights, target,
                                          [item["parts"] for item in restored] + [fresh],
                                          total * zone["max_reclaimed_pt"] // 100,
                                          zone["max_clearance"])
    return {"algorithm": "CLR", "distance": score, "target_clr": target, "blend_clr": blend,
            "restored": restored, "reclaimed_g": sum(amounts[:-1]), "total_g": total,
            "lines": [{"lot_code": code, "grams": amount}
                      for code, amount in zip([*weights, None], amounts, strict=True) if amount > 0]}
