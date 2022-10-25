import numpy as np
import math
import statistics
import pydantic
from typing import Optional, Literal, List, Dict


TaskDescription = Literal[
    "Scientific research",
    "Software engineering",
    "Hardware engineering",
    "Physical engineering",
    "Strategy",
    "Hacking",
    "Persuasion",
]

# made up parameters = numbers I made up based on my rough beliefs, can adjust based on your own beliefs and see how takeoff distribution changes
class MadeUpParameters(pydantic.BaseModel):
    # default years to cross human range means: how long, without AI automation, would it take for AIs to go from 0th to 100th percentile human capability at a typical task?
    # In favor of shorter years to cross human range: many challenging NLP benchmarks have moved through human range very quickly recently (<< 4 years)
    # In favor of longer years to cross human range: some previous AI Impacts investigations found significantly longer time cross human range (often >>4 years).
    # And maybe some less measurable NLP capabilities are also taking longer (e.g. summarization?)
    # mean + stdev based on eyeballing what looks roughly reasonable in Squiggle playground, based on uncertainty.
    # median of the distribution is 4.5, 10th percentile is 1.2, 90th percentile is 16
    default_years_to_cross_human_range_lognormal_mean: float = 1.5
    default_years_to_cross_human_range_lognormal_stdev: float = 1

    # how many years does it take to cross the human range, by default across tasks? calculated in __init__ from above
    default_years_to_cross_human_range: float = 4.5

    # how much correlation is there between how much time it takes to cross the human range across various tasks?
    # 0 = perfectly correlated, larger numbers mean higher stdev when generating this parameter for each task
    default_years_to_cross_human_range_stdev_across_tasks: float = 0.3

    # how much variation there is between starting capability level across tasks
    starting_capability_stdev: float = 0.3

    iteration_speed: str = (
        "DAY"  # how fast do we assume iteration is? can be DAY, WEEK or MONTH
    )

    # See https://docs.google.com/spreadsheets/d/1u6SsZcnAjahh7wsh0cbldVaXSHXbFLarBeu7t4jyf7E/edit#gid=0 for context
    takeoff_startpoint_conditions: List[Dict[TaskDescription, float]] = [
        {"Scientific research": 1.1, "Software engineering": 0.99, "Strategy": 0.95},
        {"Persuasion": 1},
        {"Hacking": 1.1},
        {"Strategy": 1},
        {
            "Scientific research": 1,
            "Software engineering": 1,
            "Hardware engineering": 1,
        },
        {"Physical engineering": 1},
    ]
    alignment_research_startpoint_conditions: List[Dict[TaskDescription, float]] = [
        {"Scientific research": 1.1, "Software engineering": 0.99, "Strategy": 0.95},
    ]
    takeoff_endpoint_conditions: List[Dict[TaskDescription, float]] = [
        {"Physical engineering": 3, "Strategy": 1.5},
        {"Strategy": 2, "Persuasion": 2},
        {"Strategy": 2, "Hacking": 2},
        {
            "Scientific research": 1.5,
            "Software engineering": 1.5,
            "Hardware engineering": 1.5,
            "Physical engineering": 1.5,
            "Strategy": 1.7,
            "Hacking": 1.5,
            "Persuasion": 1.7,
        },
        {
            "Scientific research": 2,
            "Software engineering": 2,
            "Hardware engineering": 2,
            "Physical engineering": 2,
            "Strategy": 2,
        },
    ]

    # How many simluations to run
    N_SIMS = 100

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
    description: TaskDescription
    capability: float = 0  # 0 = 0th percentile human, 1 = 100th percentile human, outside 0-1 = roughly extrapolating from this
    made_up_parameters: MadeUpParameters
    years_to_cross_human_range: Optional[
        float
    ] = None  # With no AI automation, how long would it take to cross human range for this task? calculated in init

    def __init__(
        self,
        made_up_parameters: MadeUpParameters,
        capability: Optional[float] = None,
        **data,
    ):
        super().__init__(
            made_up_parameters=made_up_parameters,
            capability=np.random.normal(
                0, made_up_parameters.starting_capability_stdev
            ),
            years_to_cross_human_range=max(
                np.random.normal(
                    made_up_parameters.default_years_to_cross_human_range,
                    made_up_parameters.default_years_to_cross_human_range_stdev_across_tasks,
                ),
                0.0001,
            ),
            **data,
        )

    @property
    def default_progress_in_a_day(self):
        return 1 / (self.years_to_cross_human_range * 365)


def generate_capabilities_starting_point(made_up_parameters):
    # Tasks come from Joe Carlsmith's report
    # https://docs.google.com/document/d/1smaI1lagHHcrhoi6ohdq3TYIZv0eNWWZMPEy8C8byYg/edit#heading=h.m8h4m2hdkr0u
    # with a few minor modifications
    return [
        Task(
            description="Scientific research",
            made_up_parameters=made_up_parameters,
        ),
        Task(
            description="Software engineering",
            made_up_parameters=made_up_parameters,
        ),
        Task(
            description="Hardware engineering",
            made_up_parameters=made_up_parameters,
        ),
        Task(
            description="Physical engineering",
            made_up_parameters=made_up_parameters,
        ),
        Task(
            description="Strategy",
            made_up_parameters=made_up_parameters,
        ),
        Task(
            description="Hacking",
            made_up_parameters=made_up_parameters,
        ),
        Task(
            description="Persuasion",
            made_up_parameters=made_up_parameters,
        ),
    ]


# a bit confusingly named, capabilities need to have only passed one of the conditions
def have_capabilities_passed_conditions(
    task_list: List[Task], conditions: List[Dict[TaskDescription, float]]
):
    for condition in conditions:
        condition_met = True
        for desc, threshold in condition.items():
            task = [t for t in task_list if t.description == desc][0]
            if task.capability < threshold:
                condition_met = False
                break
        if condition_met:
            return True
    return False


def capability_increase_step(
    task_list: List[Task], made_up_parameters: MadeUpParameters
):
    # speeed up based on progress in scientific research and engineering, the tasks relevant for speeding up AI research
    increase_factor = max(
        (task_list[0].capability + 1) * (task_list[1].capability + 1), 1
    )

    for task in task_list:
        task.capability = (
            task.capability + task.default_progress_in_a_day * increase_factor
        )


def main():
    years_taken = []

    for _ in range(MadeUpParameters().N_SIMS):
        made_up_parameters = MadeUpParameters()
        # print(made_up_parameters)

        task_list = generate_capabilities_starting_point(made_up_parameters)

        days = 0
        start_day = 0

        while True:
            if start_day == 0 and have_capabilities_passed_conditions(
                task_list, made_up_parameters.takeoff_startpoint_conditions
            ):
                start_day = days
            if have_capabilities_passed_conditions(
                task_list, made_up_parameters.takeoff_endpoint_conditions
            ):
                break
            capability_increase_step(task_list, made_up_parameters)
            days += 1

        takeoff_days = 0 if start_day == 0 else days - start_day
        years_taken.append(takeoff_days / 365)

    print(f"Mean: {round(sum(years_taken) / len(years_taken), 2)} years")
    print(f"Median: {round(statistics.median(years_taken), 2)} years")
    print(f"10th percentile: {round(np.percentile(years_taken, 10), 2)} years")
    print(f"90th percentile: {round(np.percentile(years_taken, 90), 2)} years")


if __name__ == "__main__":
    main()
