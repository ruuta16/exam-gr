import sys
import time

sys.setrecursionlimit(10_000)


class TooSlow(Exception):
    pass


def optimum(problem, seconds=60):
    # pilnā pārlase, tikai maziem datiem. Atgriež (rezultāts, grafiks) vai None.
    deadline = time.perf_counter() + seconds
    n, P = problem.n, problem.periods
    others, common, dist = problem.others, problem.common, problem.dist
    order = sorted(range(n), key=lambda e: -len(others[e]))
    period = [-1] * n
    best = [float("inf"), None]

    def step(i, total):
        if time.perf_counter() > deadline:
            raise TooSlow
        if total >= best[0]:
            return  # jau tagad sliktāk par labāko atrasto — tālāk nav jēgas meklēt
        if i == n:
            best[0], best[1] = total, period[:]
            return
        e = order[i]
        # pirmajam eksāmenam pietiek ar pirmo pusi periodu: apgriezts grafiks dod to pašu
        limit = (P + 1) // 2 if i == 0 else P
        options = []
        for p in range(limit):
            add, ok = 0, True
            for f, s in zip(others[e], common[e]):
                q = period[f]
                if q == p:
                    ok = False
                    break
                if q >= 0:
                    add += s * dist[abs(p - q)]
            if ok:
                options.append((add, p))
        for add, p in sorted(options):
            period[e] = p
            step(i + 1, total + add)
        period[e] = -1

    step(0, 0)
    if best[1] is None:
        return None
    return best[0] / problem.students, best[1]
