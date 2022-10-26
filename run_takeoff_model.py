import numpy as np
import math
import statistics
import pydantic
import time
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

    # TODO how fast do we assume iteration is? can be DAY, WEEK or MONTH
    # NOTE THAT ONLY DAY IS IMPLEMENTED FOR NOW, CHANGING THIS DOES NOTHING
    iteration_speed: str = "DAY"

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
    automating_alignment_startpoint_conditions: List[Dict[TaskDescription, float]] = [
        {"Scientific research": 1.05, "Software engineering": 0.99, "Strategy": 0.95},
    ]
    public_awareness_startpoint_conditions: List[Dict[TaskDescription, float]] = [
        {"Hacking": 1.1},
        {"Strategy": 1},
    ]
    economic_transformation_startpoint_conditions: List[
        Dict[TaskDescription, float]
    ] = [
        {"Strategy": 1},
        {
            "Scientific research": 1,
            "Software engineering": 1,
            "Hardware engineering": 1,
        },
        {"Physical engineering": 1},
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

    # parameter for how steep the marginal returns are
    # to increased intelligence near the human range
    # the higher the exponent, the steeper the translation
    # between progress near the human range to AI R&D
    # Would also be more small the more you think
    # AI R&D involves more uncorrelated tasks,
    # which are more bottlenecked on each other.
    # mean + stdev based on eyeballing what looks roughly reasonable in Squiggle playground, based on uncertainty.
    # median of the distribution is 4.5, 10th percentile is 1.6, 90th percentile is 12
    marginal_returns_to_intelligence_exponent_lognormal_mean: float = 1.5
    marginal_returns_to_intelligence_exponent_lognormal_stdev: float = 0.8
    marginal_returns_to_intelligence_exponent: float = 4.5

    # How many simluations to run
    N_SIMS = 1000

    def __init__(
        self,
        default_years_to_cross_human_range_lognormal_mean=1.5,
        default_years_to_cross_human_range_lognormal_stdev=1,
        marginal_returns_to_intelligence_exponent_lognormal_mean=1.5,
        marginal_returns_to_intelligence_exponent_lognormal_stdev=0.8,
        **data,
    ):
        default_years_to_cross_human_range = np.random.lognormal(
            default_years_to_cross_human_range_lognormal_mean,
            default_years_to_cross_human_range_lognormal_stdev,
        )
        marginal_returns_to_intelligence_exponent = np.random.lognormal(
            marginal_returns_to_intelligence_exponent_lognormal_mean,
            marginal_returns_to_intelligence_exponent_lognormal_stdev,
        )
        super().__init__(
            default_years_to_cross_human_range=default_years_to_cross_human_range,
            default_years_to_cross_human_range_lognormal_mean=default_years_to_cross_human_range_lognormal_mean,
            default_years_to_cross_human_range_lognormal_stdev=default_years_to_cross_human_range_lognormal_stdev,
            marginal_returns_to_intelligence_exponent=marginal_returns_to_intelligence_exponent,
            marginal_returns_to_intelligence_exponent_lognormal_mean=marginal_returns_to_intelligence_exponent_lognormal_mean,
            marginal_returns_to_intelligence_exponent_lognormal_stdev=marginal_returns_to_intelligence_exponent_lognormal_stdev,
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
    research_capability = [
        t for t in task_list if t.description == "Scientific research"
    ][0].capability
    software_eng_capability = [
        t for t in task_list if t.description == "Software engineering"
    ][0].capability
    hardware_eng_capability = [
        t for t in task_list if t.description == "Hardware engineering"
    ][0].capability

    increase_factor = 1

    # hacky check to avoid issues with complex numbers
    if min(research_capability, software_eng_capability, hardware_eng_capability) > 0:

        # calculate separate speedup in capability improvement for software improvements vs. hardware improvements
        software_multiplier = (
            (
                research_capability
                ** made_up_parameters.marginal_returns_to_intelligence_exponent
            )
            + (
                software_eng_capability
                ** made_up_parameters.marginal_returns_to_intelligence_exponent
            )
        ) / 2
        hardware_multiplier = (
            (
                research_capability
                ** made_up_parameters.marginal_returns_to_intelligence_exponent
            )
            + (
                hardware_eng_capability
                ** made_up_parameters.marginal_returns_to_intelligence_exponent
            )
        ) / 2

        increase_factor = max((software_multiplier + hardware_multiplier) / 2, 1)

        # print(
        #     research_capability,
        #     software_eng_capability,
        #     hardware_eng_capability,
        #     software_multiplier,
        #     hardware_multiplier,
        #     increase_factor,
        # )

    for task in task_list:
        task.capability = (
            task.capability + task.default_progress_in_a_day * increase_factor
        )


def main():
    s = time.time()

    any_takeoff_years_taken = []
    automating_alignment_takeoff_years_taken = []
    public_awareness_takeoff_years_taken = []
    economic_transformation_takeoff_years_taken = []

    for _ in range(MadeUpParameters().N_SIMS):
        made_up_parameters = MadeUpParameters()
        # print(made_up_parameters)

        task_list = generate_capabilities_starting_point(made_up_parameters)

        days = 0
        any_takeoff_start_day = 0
        automating_alignment_takeoff_start_day = 0
        public_awareness_takeoff_start_day = 0
        economic_transformation_takeoff_start_day = 0

        while True:
            if any_takeoff_start_day == 0 and have_capabilities_passed_conditions(
                task_list, made_up_parameters.takeoff_startpoint_conditions
            ):
                any_takeoff_start_day = days
            if (
                automating_alignment_takeoff_start_day == 0
                and have_capabilities_passed_conditions(
                    task_list,
                    made_up_parameters.automating_alignment_startpoint_conditions,
                )
            ):
                automating_alignment_takeoff_start_day = days
            if (
                public_awareness_takeoff_start_day == 0
                and have_capabilities_passed_conditions(
                    task_list, made_up_parameters.public_awareness_startpoint_conditions
                )
            ):
                public_awareness_takeoff_start_day = days
            if (
                economic_transformation_takeoff_start_day == 0
                and have_capabilities_passed_conditions(
                    task_list,
                    made_up_parameters.economic_transformation_startpoint_conditions,
                )
            ):
                economic_transformation_takeoff_start_day = days
            if have_capabilities_passed_conditions(
                task_list, made_up_parameters.takeoff_endpoint_conditions
            ):
                break
            capability_increase_step(task_list, made_up_parameters)
            days += 1

        any_takeoff_days = (
            0 if any_takeoff_start_day == 0 else days - any_takeoff_start_day
        )
        any_takeoff_years_taken.append(any_takeoff_days / 365)
        automating_alignment_takeoff_days = (
            0
            if automating_alignment_takeoff_start_day == 0
            else days - automating_alignment_takeoff_start_day
        )
        automating_alignment_takeoff_years_taken.append(
            automating_alignment_takeoff_days / 365
        )
        public_awareness_takeoff_days = (
            0
            if public_awareness_takeoff_start_day == 0
            else days - public_awareness_takeoff_start_day
        )
        public_awareness_takeoff_years_taken.append(public_awareness_takeoff_days / 365)
        economic_transformation_takeoff_days = (
            0
            if economic_transformation_takeoff_start_day == 0
            else days - economic_transformation_takeoff_start_day
        )
        economic_transformation_takeoff_years_taken.append(
            economic_transformation_takeoff_days / 365
        )

    print(
        f"Ran {made_up_parameters.N_SIMS} simluations in {round(time.time() - s, 2)} seconds\n"
    )

    print("Time from any startpoint to AI plausibly being able to disempower humanity:")
    print(
        f"Mean: {round(sum(any_takeoff_years_taken) / len(any_takeoff_years_taken), 2)} years"
    )
    print(f"Median: {round(statistics.median(any_takeoff_years_taken), 2)} years")
    print(
        f"10th percentile: {round(np.percentile(any_takeoff_years_taken, 10), 2)} years"
    )
    print(
        f"90th percentile: {round(np.percentile(any_takeoff_years_taken, 90), 2)} years\n"
    )

    print(
        "Time from very large AI-assisted alignment research speedup to AI plausibly being able to disempower humanity:"
    )
    print(
        f"Mean: {round(sum(automating_alignment_takeoff_years_taken) / len(automating_alignment_takeoff_years_taken), 2)} years"
    )
    print(
        f"Median: {round(statistics.median(automating_alignment_takeoff_years_taken), 2)} years"
    )
    print(
        f"10th percentile: {round(np.percentile(automating_alignment_takeoff_years_taken, 10), 2)} years"
    )
    print(
        f"90th percentile: {round(np.percentile(automating_alignment_takeoff_years_taken, 90), 2)} years\n"
    )

    print(
        "Time from very high public awareness of AI to AI plausibly being able to disempower humanity:"
    )
    print(
        f"Mean: {round(sum(public_awareness_takeoff_years_taken) / len(public_awareness_takeoff_years_taken), 2)} years"
    )
    print(
        f"Median: {round(statistics.median(public_awareness_takeoff_years_taken), 2)} years"
    )
    print(
        f"10th percentile: {round(np.percentile(public_awareness_takeoff_years_taken, 10), 2)} years"
    )
    print(
        f"90th percentile: {round(np.percentile(public_awareness_takeoff_years_taken, 90), 2)} years\n"
    )

    print(
        "Time from potential economic transformation (not taking into account deployment lags or regulations) to AI plausibly being able to disempower humanity:"
    )
    print(
        f"Mean: {round(sum(economic_transformation_takeoff_years_taken) / len(economic_transformation_takeoff_years_taken), 2)} years"
    )
    print(
        f"Median: {round(statistics.median(economic_transformation_takeoff_years_taken), 2)} years"
    )
    print(
        f"10th percentile: {round(np.percentile(economic_transformation_takeoff_years_taken, 10), 2)} years"
    )
    print(
        f"90th percentile: {round(np.percentile(economic_transformation_takeoff_years_taken, 90), 2)} years"
    )


if __name__ == "__main__":
    main()
