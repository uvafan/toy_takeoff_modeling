# toy_takeoff_modeling

A hacky but hopefully useful and flexible toy model of [AI takeoff](https://www.alignmentforum.org/tag/ai-takeoff).

Code written by Eli Lifland. Building off a weekend project in which I collaborated with J.J. Andrade, Trevor Levin, and Katherine Chou.

To run, clone this repo then install pyenv and poetry then:
```
pyenv install 3.9.5 && pyenv local 3.9.5
poetry install
poetry run python run_takeoff_model.py
```

With default settings the model outputs something like:
```
Ran 1000 simluations in 75.68 seconds

Time from any startpoint to AI plausibly being able to disempower humanity:
Mean: 3.66 years
Median: 1.81 years
10th percentile: 0.11 years
90th percentile: 8.54 years

Time from very large gains from AI-assisted alignment research speedup to AI plausibly being able to disempower humanity:
Mean: 1.02 years
Median: 0.29 years
10th percentile: 0.0 years
90th percentile: 2.76 years

Time from very high public awareness of AI to AI plausibly being able to disempower humanity:
Mean: 2.73 years
Median: 1.16 years
10th percentile: 0.03 years
90th percentile: 7.15 years

Time from potential economic transformation (not taking into account deployment lags or regulations) to AI plausibly being able to disempower humanity:
Mean: 3.06 years
Median: 1.42 years
10th percentile: 0.05 years
90th percentile: 7.62 years
```

You can tweak parameters based on your beliefs by changing the values in the [`MadeUpParameters` class](https://github.com/uvafan/toy_takeoff_modeling/blob/main/run_takeoff_model.py#L20).
