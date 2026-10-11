import random
import time

from construct import saturation_degree
from feasible import remove_clashes
from sa import simulated_annealing
from timetable import clashes, penalty


def solve(problem, seed, iters):
    start_time = time.perf_counter()
    rng = random.Random(seed)
    period = saturation_degree(problem, rng)
    if clashes(problem, period):
        period, left = remove_clashes(problem, period, rng)
        if left:
            return {"feasible": False, "time_s": time.perf_counter() - start_time}

    start_penalty = penalty(problem, period)
    if problem.periods > 1 and problem.n > 1 and iters > 0:
        period, _ = simulated_annealing(problem, period, rng, iters)

    elapsed = time.perf_counter() - start_time
    return {"feasible": clashes(problem, period) == 0, "period": period,
            "start_penalty": start_penalty, "penalty": penalty(problem, period),
            "time_s": elapsed}
