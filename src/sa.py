import math


def simulated_annealing(problem, start, rng, iters, T0_accept=0.1, T_end_ratio=0.001, kempe_prob=0.02):
    P, n = problem.periods, problem.n
    others, common, dist = problem.others, problem.common, problem.dist
    S = problem.students
    period = start[:]

    # busy[e][p] — cik ar e konfliktējošu eksāmenu ir periodā p (0 → e var pārcelt uz p bez konflikta)
    # cost[e][p] — e ieguldījums, ja e būtu periodā p; Δ = cost[e][b] − cost[e][a]
    busy = [[0] * P for _ in range(n)]
    cost = [[0] * P for _ in range(n)]

    # near[p] — periodi q ar pozitīvu svaru, ne tālāk par 5
    near = [[(q, dist[abs(q - p)]) for q in range(max(0, p - 5), min(P, p + 6)) if q != p] for p in range(P)]

    def place(f, s, p, sign):
        # eksāmens ar s kopīgiem studentiem ar f ienāk periodā p (sign=+1) vai iziet no tā (sign=−1)
        busy[f][p] += sign
        row = cost[f]
        for q, w in near[p]:
            row[q] += sign * s * w

    for e in range(n):
        for f, s in zip(others[e], common[e]):
            place(f, s, period[e], 1)

    def kempe_chain(e, b):
        # e pāriet uz b; eksāmeni periodā b, kas konfliktē ar e, pāriet uz e periodu a, un tā tālāk
        a = period[e]
        members, seen, stack = [e], {e}, [e]
        inner = 0  # kopīgie studenti starp pārvietotajiem eksāmeniem (katrs pāris divreiz) — to attālums nemainās
        while stack:
            x = stack.pop()
            target = b if period[x] == a else a
            if busy[x][target]:
                for f, s in zip(others[x], common[x]):
                    if period[f] == target:
                        inner += s
                        if f not in seen:
                            seen.add(f)
                            members.append(f)
                            stack.append(f)
        d = inner * dist[abs(a - b)]
        for x in members:
            old = period[x]
            d += cost[x][b if old == a else a] - cost[x][old]
        return members, d

    def random_move():
        if rng.random() >= kempe_prob:
            for _ in range(10):
                e = rng.randrange(n)
                a, row = period[e], busy[e]
                free = [p for p in range(P) if row[p] == 0 and p != a]
                if free:
                    b = free[rng.randrange(len(free))]
                    return [e], a, b, cost[e][b] - cost[e][a]
        e = rng.randrange(n)
        a = period[e]
        b = rng.randrange(P - 1)
        if b >= a:
            b += 1
        members, d = kempe_chain(e, b)
        return members, a, b, d

    def apply(members, a, b):
        for x in members:
            old = period[x]
            new = b if old == a else a
            gone, came = near[old], near[new]
            for f, s in zip(others[x], common[x]):
                row = busy[f]
                row[old] -= 1
                row[new] += 1
                row = cost[f]
                for q, w in gone:
                    row[q] -= s * w
                for q, w in came:
                    row[q] += s * w
        for x in members:
            period[x] = b if period[x] == a else a

    current = sum(cost[e][period[e]] for e in range(n)) // 2

    # sākuma temperatūra: vidējo pasliktinājumu sākumā pieņem ar varbūtību T0_accept
    worse = []
    for _ in range(200):
        d = random_move()[3]
        if d > 0:
            worse.append(d / S)
    avg_worse = sum(worse) / len(worse) if worse else 1.0
    T0 = -avg_worse / math.log(T0_accept)
    T = T0
    alpha = T_end_ratio ** (1 / iters)

    best, best_val = period[:], current
    for _ in range(iters):
        members, a, b, d = random_move()
        if d <= 0 or rng.random() < math.exp(-d / S / T):
            apply(members, a, b)
            current += d
            if current < best_val:
                best, best_val = period[:], current
        T *= alpha

    return best, best_val / S
