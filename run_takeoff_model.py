import numpy as np
import math
import statistics
import pydantic
from typing import Optional


class Task(pydantic.BaseModel):
    description: str
    capability: Optional[
        float
    ] = None  # 0 = 0th percentile human, 1 = 100th percentile human, outside 0-1 = roughly extrapolating from this
    years_to_cross_human_range_mean: Optional[
        float
    ] = None  # mean of distribution for how long it will take to cross human range
    years_to_cross_human_range_stdev: Optional[
        float
    ] = None  # standard deviation of distribution for how long it will take to cross human range
    years_to_cross_human_range: Optional[
        float
    ] = None  # With no AI automation, how long would it take to cross human range for this task

    def __init__(
        self,
        years_to_cross_human_range_mean=None,
        years_to_cross_human_range_stdev=None,
        **data,
    ):
        years_to_cross_human_range = None
        if years_to_cross_human_range_mean and years_to_cross_human_range_stdev:
            years_to_cross_human_range = np.random.normal(
                years_to_cross_human_range_mean, years_to_cross_human_range_stdev
            )
        super().__init__(
            years_to_cross_human_range=years_to_cross_human_range,
            years_to_cross_human_range_mean=years_to_cross_human_range_mean,
            **data,
        )


N_SIMS = 1000
days_taken = []
years_taken = []


def generate_takeoff_start():
    # skills are research, eng, strategy, hacking, persuasion
    # for simpllicitly let's treat them all as the same for now
    # Numbers come from https://docs.google.com/spreadsheets/d/1VdiVeaTHimvz5SzDyghwxsD1D4tcr7KZULL0KiOeDPk/edit#gid=0
    log_average_capabilities = np.random.normal(0.54, 0.16)
    average_exp_capabilites = 10 ** log_average_capabilities
    rand_vars = [np.random.uniform() for _ in range(5)]
    normalized_exp_capabilties = [tc / sum(rand_vars) for tc in rand_vars]
    scaled_tcs = [math.log10(tc) for tc in normalized_exp_capabilties]
    return [
        Task(description="Scientific research", capability=scaled_tcs[0]),
        Task(description="Engineering", capability=scaled_tcs[1]),
        Task(description="Strategy", capability=scaled_tcs[2]),
        Task(description="Hacking", capability=scaled_tcs[3]),
        Task(description="Persuasion", capability=scaled_tcs[4]),
    ]


def generate_takeoff_end():
    # skills are research, eng, strategy, hacking, persuasion
    # for simpllicitly let's treat them all as the same for now
    # Numbers come from https://docs.google.com/spreadsheets/d/1VdiVeaTHimvz5SzDyghwxsD1D4tcr7KZULL0KiOeDPk/edit#gid=0
    log_average_capabilities = np.random.normal(1.41, 0.60)
    average_exp_capabilites = 10 ** log_average_capabilities
    rand_vars = [np.random.uniform() for _ in range(5)]
    normalized_exp_capabilties = [tc / sum(rand_vars) for tc in rand_vars]
    scaled_tcs = [math.log10(tc) for tc in normalized_exp_capabilties]
    return [
        Task(description="Scientific research", capability=scaled_tcs[0]),
        Task(description="Engineering", capability=scaled_tcs[1]),
        Task(description="Strategy", capability=scaled_tcs[2]),
        Task(description="Hacking", capability=scaled_tcs[3]),
        Task(description="Persuasion", capability=scaled_tcs[4]),
    ]


def is_takeoff_over(tc_cur, tc_end):
    for i in range(len(tc_cur)):
        if tc_cur[i].capability < tc_end[i].capability:
            return False
    return True


def capability_increase_step(tc_cur):
    default_yrs_to_cross_human_range = 4
    default_progress_in_day = 1 / (default_yrs_to_cross_human_range * 365)
    # speeed up based on progress relevant for speeding up AI research
    increase_factor = max((tc_cur[0].capability + 1) * (tc_cur[1].capability + 1), 1)

    for task in tc_cur:
        task.capability = task.capability + default_progress_in_day * increase_factor


for _ in range(N_SIMS):
    tc_0 = generate_takeoff_start()
    tc_end = generate_takeoff_end()

    days = 0
    tc_cur = tc_0

    while True:
        if is_takeoff_over(tc_cur, tc_end):
            break
        capability_increase_step(tc_cur)
        days += 1

    days_taken.append(days)
    years_taken.append(days / 365)

print(f"Mean: {round(sum(years_taken) / len(years_taken), 2)} years")
print(f"Median: {round(statistics.median(years_taken), 2)} years")
print(f"10th percentile: {round(np.percentile(years_taken, 10), 2)} years")
print(f"90th percentile: {round(np.percentile(years_taken, 90), 2)} years")
