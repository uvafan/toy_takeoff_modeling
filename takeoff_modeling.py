import numpy as np
import math
import statistics

N_SIMS = 1000
days_taken = []

def generate_takeoff_start():
    # skills are research, eng, strategy, hacking, persuasion
    # for simpllicitly let's treat them all as the same for now
    # Numbers come from https://docs.google.com/spreadsheets/d/1VdiVeaTHimvz5SzDyghwxsD1D4tcr7KZULL0KiOeDPk/edit#gid=0
    log_average_capabilities = np.random.normal(.54, .16)
    average_exp_capabilites = 10 ** log_average_capabilities
    rand_vars = [np.random.uniform() for _ in range(5)]
    normalized_exp_capabilties = [tc / sum(rand_vars) for tc in rand_vars]
    scaled_tcs = [math.log10(tc) for tc in normalized_exp_capabilties]
    return scaled_tcs

def generate_takeoff_end():
    # skills are research, eng, strategy, hacking, persuasion
    # for simpllicitly let's treat them all as the same for now
    # Numbers come from https://docs.google.com/spreadsheets/d/1VdiVeaTHimvz5SzDyghwxsD1D4tcr7KZULL0KiOeDPk/edit#gid=0
    log_average_capabilities = np.random.normal(1.41, .60)
    average_exp_capabilites = 10 ** log_average_capabilities
    rand_vars = [np.random.uniform() for _ in range(5)]
    normalized_exp_capabilties = [tc / sum(rand_vars) for tc in rand_vars]
    scaled_tcs = [math.log10(tc) for tc in normalized_exp_capabilties]
    return scaled_tcs

def is_takeoff_over(tc_cur, tc_end):
    for i in range(len(tc_cur)):
        if tc_cur[i] < tc_end[i]:
            return False
    return True

def capability_increase_step(tc_cur):
    default_yrs_to_cross_human_range = 4
    default_progress_in_day = 1 / (default_yrs_to_cross_human_range * 365)
    # speeed up based on progress relevant for speeding up AI research
    increase_factor = max((tc_cur[0] + 1) * (tc_cur[1] + 1), 1)
    return list(map(lambda tc: tc + default_progress_in_day * increase_factor, tc_cur))

for _ in range(N_SIMS):
    tc_0 = generate_takeoff_start()
    tc_end = generate_takeoff_end()
    
    days = 0
    tc_cur = tc_0

    while True:
        if is_takeoff_over(tc_cur, tc_end):
            break
        tc_cur = capability_increase_step(tc_cur)
        days += 1
    
    days_taken.append(days)

print(f"Mean: {sum(days_taken) / len(days_taken)}")
print(f"Median: {statistics.median(days_taken)}")
print(f"10th percentile: {np.percentile(days_taken, 10)}")
print(f"90th percentile: {np.percentile(days_taken, 90)}")