def saturation_degree(problem, rng):
    # nākamais — kam vismazāk brīvo periodu; liek brīvajā periodā ar mazāko vērtību
    # ja brīva perioda nav, liek tur, kur mazāk konfliktu
    n, P = problem.n, problem.periods
    period = [-1] * n
    busy = [[0] * P for _ in range(n)]  # busy[e][p] — cik ar e konfliktējošu eksāmenu jau ir periodā p
    free = [P] * n
    degree = [len(o) for o in problem.others]
    tie = [rng.random() for _ in range(n)]
    todo = set(range(n))

    while todo:
        e = min(todo, key=lambda x: (free[x], -degree[x], tie[x]))
        todo.remove(e)
        options = [p for p in range(P) if busy[e][p] == 0] or range(P)

        def cost(p):
            c = sum(s * problem.dist[abs(p - period[f])]
                    for f, s in zip(problem.others[e], problem.common[e]) if period[f] >= 0)
            return (busy[e][p], c)

        best = min(options, key=cost)
        period[e] = best
        for f in problem.others[e]:
            if busy[f][best] == 0:
                free[f] -= 1
            busy[f][best] += 1
    return period
