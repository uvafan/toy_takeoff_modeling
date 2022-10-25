import numpy as np
import math
import statistics
import pydantic
from typing import Optional

# made up parameters = numbers I made up, can adjust based on your own beliefs and see how takeoff distribution changes


class MadeUpParameters(pydantic.BaseModel):
    # default years to cross human range means: how long, without AI automation, would it take for AIs to go from 0th to 100th percentile human capability at a typical task?
    # In favor of shorter years to cross human range: many challenging NLP benchmarks have moved through human range very quickly recently (<< 4 years)
    # In favor of longer years to cross human range: some previous AI Impacts investigations found significantly longer time cross human range (often >>4 years).
    # And maybe some less measurable NLP capabilities are also taking longer (e.g. summarization?)
    # mean + stdev based on eyeballing what looks roughly reasonable in Squiggle playground, based on uncertainty.
    # mean of the distribution is 4.5, 10th percentile is 1.2, 90th percentile is 16
    default_years_to_cross_human_range_lognormal_mean: float = 1.5
    default_years_to_cross_human_range_lognormal_stdev: float = 1
    default_years_to_cross_human_range: Optional[
        float
    ] = None  # how many years does it take to cross the human range, by default across tasks? calculated in __init__ from above
    iteration_speed: str = (
        "DAY"  # how fast do we assume iteration is? can be DAY, WEEK or MONTH
    )

    def __init__(
        self,
        default_years_to_cross_human_range_lognormal_mean=1.5,
        default_years_to_cross_human_range_lognormal_stdev=1,
        **data,
    ):
        default_years_to_cross_human_range = None
        default_years_to_cross_human_range = np.random.lognormal(
            default_years_to_cross_human_range_lognormal_mean,
            default_years_to_cross_human_range_lognormal_stdev,
        )
        super().__init__(
            default_years_to_cross_human_range=default_years_to_cross_human_range,
            default_years_to_cross_human_range_lognormal_mean=default_years_to_cross_human_range_lognormal_mean,
            default_years_to_cross_human_range_lognormal_stdev=default_years_to_cross_human_range_lognormal_stdev,
            **data,
        )


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
            years_to_cross_human_range_stdev=years_to_cross_human_range_stdev,
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


def capability_increase_step(tc_cur, made_up_parameters):
    default_progress_in_day = 1 / (
        made_up_parameters.default_years_to_cross_human_range * 365
    )
    # speeed up based on progress relevant for speeding up AI research
    increase_factor = max((tc_cur[0].capability + 1) * (tc_cur[1].capability + 1), 1)

    for task in tc_cur:
        task.capability = task.capability + default_progress_in_day * increase_factor


for _ in range(N_SIMS):
    made_up_parameters = MadeUpParameters()
    print(made_up_parameters)

    tc_0 = generate_takeoff_start()
    tc_end = generate_takeoff_end()

    days = 0
    tc_cur = tc_0

    while True:
        if is_takeoff_over(tc_cur, tc_end):
            break
        capability_increase_step(tc_cur, made_up_parameters)
        days += 1

    days_taken.append(days)
    years_taken.append(days / 365)

print(f"Mean: {round(sum(years_taken) / len(years_taken), 2)} years")
print(f"Median: {round(statistics.median(years_taken), 2)} years")
print(f"10th percentile: {round(np.percentile(years_taken, 10), 2)} years")
print(f"90th percentile: {round(np.percentile(years_taken, 90), 2)} years")
