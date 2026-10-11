import argparse
import csv
import os
import sys

from exact import optimum
from instances import INSTANCES, SMALL
from solver import solve
from timetable import ExamProblem, read_students, student_clashes, student_penalty

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COLUMNS = ["instance", "exams", "students", "periods", "density", "reference", "ref_type", "start", "best",
           "avg", "worst", "gap_best_pct", "gap_avg_pct", "hits", "avg_time_s", "max_time_s", "clashes"]


def run_instance(name, runs, iters):
    P, best_known = INSTANCES[name]
    students = read_students(os.path.join(ROOT, "data", name + ".stu"))
    problem = ExamProblem(students, P, name)
    if name in SMALL:
        ref, ref_type = optimum(problem)[0], "optimums"
    else:
        ref, ref_type = best_known, "labākais zināmais"

    results = []
    for seed in range(runs):
        r = solve(problem, seed, iters)
        # pārbaude pa studentiem: nav konfliktu un abi aprēķini sakrīt
        if not r["feasible"] or student_clashes(students, problem, r["period"]):
            raise SystemExit(f"Kļūda: {name} — grafikā ir konflikti")
        if abs(student_penalty(students, problem, r["period"]) - r["penalty"]) > 1e-9:
            raise SystemExit(f"Kļūda: {name} — soda aprēķini nesakrīt")
        results.append(r)

    pens = [r["penalty"] for r in results]
    times = [r["time_s"] for r in results]
    best, avg = min(pens), sum(pens) / runs

    def gap(x):
        return round((x - ref) / ref * 100, 2) if ref else ""

    return {
        "instance": name,
        "exams": problem.n,
        "students": problem.students,
        "periods": P,
        "density": round(2 * problem.pairs / (problem.n * (problem.n - 1)), 2),
        "reference": round(ref, 2) if ref is not None else "",
        "ref_type": ref_type if ref is not None else "nav publicēts",
        "start": round(sum(r["start_penalty"] for r in results) / runs, 2),
        "best": round(best, 2),
        "avg": round(avg, 2),
        "worst": round(max(pens), 2),
        "gap_best_pct": gap(best),
        "gap_avg_pct": gap(avg),
        "hits": f"{sum(abs(p - ref) < 1e-9 for p in pens)}/{runs}" if name in SMALL else "",
        "avg_time_s": round(sum(times) / runs, 2),
        "max_time_s": round(max(times), 2),
        "clashes": 0,
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--iters", type=int, default=2_000_000, help="SA iterācijas Toronto datiem")
    parser.add_argument("--iters-small", type=int, default=50_000, help="SA iterācijas mazajiem datiem")
    parser.add_argument("--only", default="")
    parser.add_argument("--out", default="results")
    args = parser.parse_args()
    if args.runs < 1 or args.iters < 1 or args.iters_small < 1:
        parser.error("--runs un --iters jābūt vismaz 1")
    names = args.only.split(",") if args.only else list(INSTANCES)
    missing = [n for n in names if n not in INSTANCES or not os.path.exists(os.path.join(ROOT, "data", n + ".stu"))]
    if missing:
        parser.error(f"nav šādu testa datu: {', '.join(missing)}")

    info = (f"SA: sākumā sliktāku gājienu pieņem ar varbūtību 0,1; beigu temperatūra = sākuma/1000\n"
            f"Iterācijas: Toronto {args.iters}, mazie {args.iters_small}; {args.runs} palaišanas (seed 0..{args.runs - 1})")
    print(info)
    rows = []
    for name in names:
        iters = args.iters_small if name in SMALL else args.iters
        row = run_instance(name, args.runs, iters)
        rows.append(row)
        ref = f"{row['ref_type']} {row['reference']}" if row["reference"] != "" else "labākais zināmais nav publicēts"
        gap = f"{row['gap_best_pct']}%" if row["gap_best_pct"] != "" else "—"
        print(f"{name:<8} eks.={row['exams']:<5} per.={row['periods']:<3} sākumā={row['start']:<7} "
              f"SA lab.={row['best']:<7} vid.={row['avg']:<7} {ref:<32} atšķ.={gap:<7} "
              f"laiks={row['avg_time_s']} s", flush=True)

    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    path = os.path.join(ROOT, "results", args.out)
    with open(path + ".csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    with open(path + ".md", "w", encoding="utf-8") as f:
        f.write(info + "\n\n")
        f.write("| " + " | ".join(COLUMNS) + " |\n")
        f.write("|" + " --- |" * len(COLUMNS) + "\n")
        for row in rows:
            f.write("| " + " | ".join(str(row[c]) for c in COLUMNS) + " |\n")
    print(f"Saglabāts results/{args.out}.csv un results/{args.out}.md")


if __name__ == "__main__":
    main()
