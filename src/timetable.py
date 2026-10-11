import os

WEIGHTS = {1: 16, 2: 8, 3: 4, 4: 2, 5: 1}


class ExamProblem:
    def __init__(self, students, periods, name=""):
        self.name = name
        self.periods = periods
        self.exams = sorted({e for s in students for e in s})
        self.n = len(self.exams)
        self.students = len(students)
        index = {e: i for i, e in enumerate(self.exams)}

        # shared[e][f] — cik studentu kārto gan eksāmenu e, gan f
        shared = [{} for _ in range(self.n)]
        for s in students:
            ids = sorted({index[e] for e in s})
            for a in range(len(ids)):
                for b in range(a + 1, len(ids)):
                    u, v = ids[a], ids[b]
                    shared[u][v] = shared[u].get(v, 0) + 1
                    shared[v][u] = shared[v].get(u, 0) + 1
        self.others = [list(d) for d in shared]          # eksāmeni ar kopīgiem studentiem
        self.common = [list(d.values()) for d in shared]  # kopīgo studentu skaits
        self.pairs = sum(len(d) for d in shared) // 2
        # dist[0] — konflikts, to neskaita
        self.dist = [WEIGHTS.get(d, 0) for d in range(max(periods, 6))]


def read_students(path):
    # viena rinda = viens students un viņa eksāmeni
    with open(path, encoding="utf-8") as f:
        students = [line.split() for line in f if line.strip()]
    if not students:
        raise ValueError(f"failā '{path}' nav neviena studenta")
    return students


def instance_name(path):
    return os.path.splitext(os.path.basename(path))[0]


def raw_penalty(problem, period):
    total = 0
    for e in range(problem.n):
        pe = period[e]
        for f, s in zip(problem.others[e], problem.common[e]):
            if f > e:
                total += s * problem.dist[abs(pe - period[f])]
    return total


def penalty(problem, period):
    return raw_penalty(problem, period) / problem.students


def clashes(problem, period):
    # eksāmenu pāri ar kopīgiem studentiem vienā periodā
    return sum(1 for e in range(problem.n) for f in problem.others[e] if f > e and period[e] == period[f])


def student_clashes(students, problem, period):
    # neatkarīga pārbaude: cik studentiem ir divi eksāmeni vienā laikā
    index = {e: i for i, e in enumerate(problem.exams)}
    bad = 0
    for s in students:
        used = [period[index[e]] for e in set(s)]
        if len(used) != len(set(used)):
            bad += 1
    return bad


def student_penalty(students, problem, period):
    # tas pats aprēķins pa studentiem, pārbaudei
    index = {e: i for i, e in enumerate(problem.exams)}
    total = 0
    for s in students:
        ps = sorted(period[index[e]] for e in set(s))
        for a in range(len(ps)):
            for b in range(a + 1, len(ps)):
                total += WEIGHTS.get(ps[b] - ps[a], 0)
    return total / len(students)


def read_solution(path, problem):
    # rindā "eksāmena numurs periods"
    index = {int(e): i for i, e in enumerate(problem.exams)}
    period = [-1] * problem.n
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                if int(parts[0]) not in index:
                    raise ValueError(f"fails '{path}' neatbilst datiem (eksāmens {parts[0]} nav datos)")
                period[index[int(parts[0])]] = int(parts[1])
    return period
