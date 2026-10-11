import os
import subprocess
import sys
import tempfile

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
DATA = os.path.join(ROOT, "data")
SOL = os.path.join(DATA, "solutions")

# (skripts, argumenti, ko sagaida izvadē)
CASES = [
    # pareiza ievade: rezultāts = precīzais optimums
    ("schedule.py", ["--periods", "3", "Mat,Fiz,Prog"], "Sods uz vienu studentu: 40.00"),
    ("schedule.py", ["--periods", "6", "Mat,Fiz,Prog"], "Sods uz vienu studentu: 13.00"),
    ("schedule.py", ["--periods", "2", "Mat,Fiz", "Prog,Angl"], "Sods uz vienu studentu: 16.00"),
    ("schedule.py", ["--periods", "7", "Mat,Fiz", "Prog,Angl"], "Sods uz vienu studentu: 0.00"),
    ("schedule.py", ["--periods", "1", "Mat"], "Sods uz vienu studentu: 0.00"),
    ("schedule.py", ["--periods", "3", "Mat,Fiz", "Mat,Fiz"], "Sods uz vienu studentu: 8.00"),
    ("schedule.py", ["--periods", "3", "Mat,Mat,Fiz"], "Sods uz vienu studentu: 8.00"),
    ("schedule.py", ["--periods", "2", "Mat, Fiz"], "Sods uz vienu studentu: 16.00"),
    ("schedule.py", ["--periods", "4", "Mat,Fiz,Prog", "Mat,Angl", "Fiz,Ekon", "Prog,Angl,Vēst", "Ekon,Vēst",
                     "Mat,Ekon"], "Sods uz vienu studentu: 13.33"),
    ("schedule.py", ["--periods", "4", "Mat,Fiz,Prog", "Mat,Angl", "Fiz,Ekon", "Prog,Angl,Vēst", "Ekon,Vēst",
                     "Mat,Ekon"], "kopā 80 / 6 = 13.33"),
    ("schedule.py", ["--periods", "5", "Mat,Fiz,Angl", "Prog,DB,Angl", "Mat,Prog"], "Sods uz vienu studentu: 12.67"),
    ("schedule.py", [os.path.join(DATA, "mazs_06.stu")], "Sods uz vienu studentu: 13.00"),
    ("schedule.py", [os.path.join(DATA, "mazs_09.stu")], "Sods uz vienu studentu: 10.44"),
    ("schedule.py", [os.path.join(DATA, "hec92.stu")], "Nevienam studentam nav 2 eksāmenu vienā laikā: ✅"),
    # hard ierobežojums: ar par maz periodiem derīga grafika nav
    ("schedule.py", ["--periods", "2", "Mat,Fiz", "Fiz,Prog", "Mat,Prog"], "nav iespējams"),
    ("schedule.py", ["--periods", "2", "Mat,Fiz,Prog"], "nav iespējams"),
    # publicētie grafiki dod publicēto rezultātu
    ("schedule.py", [os.path.join(DATA, "yor83.stu"), "--solution", os.path.join(SOL, "yor83.sol")], "Sods uz vienu studentu: 34.84"),
    ("schedule.py", [os.path.join(DATA, "car91.stu"), "--solution", os.path.join(SOL, "car91.sol")], "Sods uz vienu studentu: 4.42"),
    ("schedule.py", [os.path.join(DATA, "car92.stu"), "--solution", os.path.join(SOL, "car92.sol")], "Sods uz vienu studentu: 3.74"),
    ("schedule.py", [os.path.join(DATA, "tre92.stu"), "--solution", os.path.join(SOL, "tre92.sol")], "Sods uz vienu studentu: 7.75"),
    ("schedule.py", [os.path.join(DATA, "uta92.stu"), "--solution", os.path.join(SOL, "uta92.sol")], "Sods uz vienu studentu: 3.06"),
    # kļūdaina ievade
    ("schedule.py", ["--periods", "3", "Mat,,Fiz"], "nepareizs students"),
    ("schedule.py", ["--periods", "3", ""], "nepareizs students"),
    ("schedule.py", ["Mat,Fiz"], "norādi periodu skaitu"),
    ("schedule.py", ["--periods", "0", "Mat,Fiz"], "--periods jābūt vismaz 1"),
    ("schedule.py", ["nav.stu"], "nevar atvērt failu"),
    ("schedule.py", ["EMPTY"], "nav neviena studenta"),
    ("schedule.py", [os.path.join(DATA, "hec92.stu"), "--solution", os.path.join(SOL, "yor83.sol")], "neatbilst datiem"),
    ("run_tests.py", ["--runs", "0"], "jābūt vismaz 1"),
    ("run_tests.py", ["--only", "nav"], "nav šādu testa datu"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    passed = 0
    with tempfile.TemporaryDirectory() as tmp:
        empty = os.path.join(tmp, "EMPTY.stu")
        open(empty, "w").close()

        for script, args, expected in CASES:
            args = [empty if a == "EMPTY" else a for a in args]
            run = subprocess.run([sys.executable, "-B", os.path.join(SRC, script), *args],
                                 capture_output=True, text=True, encoding="utf-8", env=env)
            output = run.stdout + run.stderr
            ok = expected in output and "Traceback" not in output
            passed += ok
            # pēdiņas tikai tukšam argumentam vai argumentam ar atstarpi
            shown = " ".join(os.path.basename(a) if a.endswith((".stu", ".sol")) else f'"{a}"' if a == "" or " " in a
                             else a for a in args)
            print(f"{'✅' if ok else '❌'} {script:<12} {shown:<48} → sagaida: {expected}")

    print(f"\nIzdevās {passed} no {len(CASES)}")
    sys.exit(0 if passed == len(CASES) else 1)


if __name__ == "__main__":
    main()
