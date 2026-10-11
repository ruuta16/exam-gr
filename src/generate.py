import os
import random

from instances import SMALL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUBJECTS = ["Mat", "Fiz", "Prog", "Angl", "Ekon", "Vēst", "Ķīm", "Bio", "DB", "Tīkli", "Stat", "Filoz"]

# nosaukums: (eksāmeni, studenti); periodu skaits — instances.py
SIZES = {"mazs_06": (6, 10), "mazs_09": (9, 25), "mazs_12": (12, 40)}


def generate(exams, students, seed):
    # katrs students kārto 2–3 nejaušus eksāmenus; katram eksāmenam vismaz viens students
    rng = random.Random(seed)
    names = SUBJECTS[:exams]
    rows = [rng.sample(names, rng.randint(2, 3)) for _ in range(students)]
    for e in names:
        if not any(e in r for r in rows):
            rng.choice([r for r in rows if len(r) < 4]).append(e)
    return rows


def main():
    for name, (exams, students) in SIZES.items():
        rows = generate(exams, students, seed=exams)
        path = os.path.join(ROOT, "data", name + ".stu")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(" ".join(r) for r in rows) + "\n")
        print(f"Saglabāts data/{name}.stu: {exams} eksāmeni, {students} studenti, {SMALL[name][0]} periodi")


if __name__ == "__main__":
    main()
