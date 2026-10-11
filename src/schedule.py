import argparse
import os
import sys

from exact import TooSlow, optimum
from instances import INSTANCES
from solver import solve
from timetable import (WEIGHTS, ExamProblem, instance_name, penalty, read_solution, read_students, student_clashes,
                       student_penalty)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITERS = 50_000
GRID_MAX_STUDENTS, GRID_MAX_PERIODS = 40, 12  # studentu režģi rāda tikai maziem datiem

# (apraksts, studenti, periodu skaits)
EXAMPLES = [
    ("students ar 3 eksāmeniem, 3 periodi", ["Mat,Fiz,Prog"], 3),
    ("tas pats students, 6 periodi", ["Mat,Fiz,Prog"], 6),
    ("2 grupas bez kopīgiem eksāmeniem, 2 periodi", ["Mat,Fiz", "Prog,Angl"], 2),
    ("kurss: 6 studenti, 6 eksāmeni, 4 periodi",
     ["Mat,Fiz,Prog", "Mat,Angl", "Fiz,Ekon", "Prog,Angl,Vēst", "Ekon,Vēst", "Mat,Ekon"], 4),
    ("2 kursi ar kopīgu angļu valodu, 5 periodi", ["Mat,Fiz,Angl", "Prog,DB,Angl", "Mat,Prog"], 5),
    ("par maz periodu: 3 eksāmeni, 2 periodi", ["Mat,Fiz", "Fiz,Prog", "Mat,Prog"], 2),
]
FILES = ["mazs_06", "mazs_09", "mazs_12"]


def parse(args):
    # katrs arguments = viens students, eksāmeni atdalīti ar komatu
    students = []
    for arg in args:
        exams = [e.strip() for e in arg.split(",")]
        if "" in exams:
            raise ValueError(f"nepareizs students '{arg}' — eksāmeni jāatdala ar komatu, piem. Mat,Fiz")
        students.append(exams)
    return students


def exact_or_none(problem):
    # precīzais optimums tikai maziem datiem; "nav" — derīga grafika nav, None — nav pārbaudīts
    if problem.n > 12:
        return None
    try:
        result = optimum(problem, seconds=30)
    except TooSlow:
        return None
    return "nav" if result is None else result[0]


def run_examples():
    cases = [(name, parse(s), P) for name, s, P in EXAMPLES]
    for name in FILES:
        cases.append((name, read_students(os.path.join(ROOT, "data", name + ".stu")), INSTANCES[name][0]))

    print(f"{'Piemērs':<46} {'eks.':>4} {'stud.':>5} {'per.':>4} {'SA sods':>8} {'optimums':>8}")
    for name, students, P in cases:
        problem = ExamProblem(students, P, name)
        result = solve(problem, 0, ITERS)
        best = exact_or_none(problem)
        if not result["feasible"]:
            sa_text = "nav"
            mark = "✅ derīga grafika nav (pierādīts ar pilno pārlasi)" if best == "nav" else "❌ neatrada derīgu"
        else:
            ok = student_clashes(students, problem, result["period"]) == 0
            sa_text = f"{result['penalty']:.2f}"
            if not ok:
                mark = "❌ konflikts"
            elif best is None:
                mark = "✅ (optimums nav pārbaudīts)"
            else:
                mark = "✅ optimums" if abs(result["penalty"] - best) < 1e-9 else "✅ derīgs, bet nav optimums"
        best_text = best if isinstance(best, str) else ("?" if best is None else f"{best:.2f}")
        print(f"{name:<46} {problem.n:>4} {len(students):>5} {P:>4} {sa_text:>8} {best_text:>8}  {mark}")


def show(students, P, name=""):
    problem = ExamProblem(students, P, name)
    print(f"Eksāmeni: {problem.n}, studenti: {len(students)}, periodi: {P}, "
          f"eksāmenu pāri ar kopīgiem studentiem: {problem.pairs}")
    result = solve(problem, 0, ITERS if problem.n <= 200 else 500_000)
    if not result["feasible"]:
        best = exact_or_none(problem)
        why = "nav iespējams (pierādīts ar pilno pārlasi)" if best == "nav" else "neizdevās atrast"
        print(f"Grafiks bez konfliktiem ar {P} periodiem: {why}")
        return
    period = result["period"]
    print("Grafiks:")
    for p in range(P):
        in_period = [problem.exams[e] for e in range(problem.n) if period[e] == p]
        text = ", ".join(in_period) if problem.n <= 60 else f"{len(in_period)} eksāmeni"
        print(f"  {p + 1}. periods: {text or '—'}")
    if len(students) <= GRID_MAX_STUDENTS and P <= GRID_MAX_PERIODS:
        student_grid(students, problem, period)
    clashes = student_clashes(students, problem, period)
    print(f"Nevienam studentam nav 2 eksāmenu vienā laikā: {'✅' if clashes == 0 else f'❌ ({clashes})'}")
    best = exact_or_none(problem)
    best_text = "nav pārbaudīts — par lielu" if best is None else f"{best:.2f}"
    print(f"Sods uz vienu studentu: {result['penalty']:.2f} (sākuma grafikam {result['start_penalty']:.2f}), "
          f"mazākais iespējamais: {best_text}, laiks: {result['time_s']:.2f} s")


def student_grid(students, problem, period):
    # rinda = students, kolonna = periods; pēdējā kolonnā šī studenta rezultāts
    index = {e: i for i, e in enumerate(problem.exams)}
    P = problem.periods
    rows, total = [], 0
    for s in students:
        exams = sorted(set(s), key=lambda e: period[index[e]])
        cells = ["·"] * P
        for e in exams:
            p = period[index[e]]
            cells[p] = e if cells[p] == "·" else cells[p] + "+" + e
        ps = [period[index[e]] for e in exams]
        cost = sum(WEIGHTS.get(ps[b] - ps[a], 0) for a in range(len(ps)) for b in range(a + 1, len(ps)))
        total += cost
        rows.append((cells, cost))

    width = max(4, max(len(c) for cells, _ in rows for c in cells)) + 2
    name_w = len(f"S{len(students)}") + 2
    print("Studentu grafiks (· — nav eksāmena):")
    print(" " * (name_w + 2) + "".join(f"{p + 1}.".ljust(width) for p in range(P)) + "sods")
    for i, (cells, cost) in enumerate(rows, 1):
        print(f"  {f'S{i}':<{name_w}}" + "".join(c.ljust(width) for c in cells) + str(cost))
    print(" " * (name_w + 2 + width * P - 5) + f"kopā {total} / {len(students)} = {total / len(students):.2f}")


def check_solution(students, P, path, name):
    # novērtē gatavu grafiku no .sol faila (piem. publicētu literatūrā)
    problem = ExamProblem(students, P, name)
    period = read_solution(path, problem)
    if -1 in period or max(period) >= P:
        raise ValueError(f"fails '{path}' neatbilst datiem (trūkst eksāmenu vai periods ≥ {P})")
    print(f"Grafiks no {os.path.basename(path)}: konfliktējoši studenti: {student_clashes(students, problem, period)}")
    print(f"Sods uz vienu studentu: {penalty(problem, period):.2f} "
          f"(pārbaude pa studentiem: {student_penalty(students, problem, period):.2f})")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Eksāmenu grafika sastādīšana ar simulēto rūdīšanu")
    parser.add_argument("students", nargs="*", help="studenti, piem. Mat,Fiz Fiz,Prog, vai .stu fails")
    parser.add_argument("--periods", type=int, help="periodu skaits sesijā")
    parser.add_argument("--solution", help=".sol fails, kura sodu aprēķināt")
    args = parser.parse_args()

    if not args.students:
        run_examples()
        return
    if args.periods is not None and args.periods < 1:
        parser.error("--periods jābūt vismaz 1")
    try:
        name = ""
        if args.students[0].endswith(".stu"):
            if len(args.students) > 1:
                parser.error("norādi vai nu failu, vai studentus, ne abus")
            students = read_students(args.students[0])
            name = instance_name(args.students[0])
        else:
            students = parse(args.students)
        P = args.periods or INSTANCES.get(name, (None,))[0]
        if P is None:
            parser.error("norādi periodu skaitu, piem. --periods 4")
        if args.solution:
            check_solution(students, P, args.solution, name)
        else:
            show(students, P, name)
    except OSError as e:
        parser.error(f"nevar atvērt failu '{e.filename}'")
    except ValueError as e:
        parser.error(str(e))


if __name__ == "__main__":
    main()
