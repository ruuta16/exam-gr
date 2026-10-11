import math


def remove_clashes(problem, start, rng, max_iters=2_000_000, T0=0.5, T_min=0.001):
    # SA, kas novērš konfliktus (studentam 2 eksāmeni vienā periodā), ja sākuma grafikā tādi palikuši.
    # f = eksāmenu pāru skaits ar kopīgiem studentiem vienā periodā; mērķis f = 0.
    P = problem.periods
    others = problem.others
    period = start[:]
    alpha = (T_min / T0) ** (1 / max_iters)

    # conf[e] — cik ar e konfliktējošu eksāmenu ir tajā pašā periodā
    conf = [sum(1 for f in others[e] if period[f] == period[e]) for e in range(problem.n)]
    f_val = sum(conf) // 2

    # konfliktējošie eksāmeni: saraksts + pozīcijas, lai izvēle būtu O(1)
    bad, pos = [], {}

    def add(e):
        if e not in pos:
            pos[e] = len(bad)
            bad.append(e)

    def remove(e):
        i = pos.pop(e, None)
        if i is not None:
            last = bad.pop()
            if i < len(bad):
                bad[i] = last
                pos[last] = i

    for e in range(problem.n):
        if conf[e] > 0:
            add(e)

    best, best_f = period[:], f_val
    T, it = T0, 0
    while f_val > 0 and P > 1 and it < max_iters:
        e = bad[rng.randrange(len(bad))]
        old = period[e]
        new = rng.randrange(P - 1)
        if new >= old:
            new += 1
        same_new = sum(1 for f in others[e] if period[f] == new)
        delta = same_new - conf[e]

        if delta <= 0 or rng.random() < math.exp(-delta / T):
            for f in others[e]:
                if period[f] == old:
                    conf[f] -= 1
                    if conf[f] == 0:
                        remove(f)
                elif period[f] == new:
                    conf[f] += 1
                    add(f)
            period[e] = new
            conf[e] = same_new
            if same_new == 0:
                remove(e)
            f_val += delta
            if f_val < best_f:
                best, best_f = period[:], f_val
        T *= alpha
        it += 1
    return best, best_f
