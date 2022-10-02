import numpy as np

N_SIMS = 1000
days_taken = []

def is_takeoff_over(tc_cur, tc_end):
    for i in range(len(tc_cur)):
        if tc_cur[i] < tc_end[i]:
            return False
    return True

def capability_increase_step(tc_cur):
    default_yrs_to_cross_human_range = 4
    default_progress_in_day = 1 / (default_yrs_to_cross_human_range * 365)
    # speeed up based on progress relevant for speeding up 
    # AI research
    increase_factor = max((tc_cur[1] + 1) * (tc_cur[1] + 1), 1)
    return list(map(lambda tc: tc + default_progress_in_day * increase_factor, tc_cur))

for _ in range(N_SIMS):
    persuasion_takeoff_start = np.random.normal(-.5, 1.5)
    coding_takeoff_start = np.random.normal(-.5, 1.5)
    tc_0 = [persuasion_takeoff_start, coding_takeoff_start]

    persuasion_takeoff_end = np.random.normal(3, 2)
    coding_takeoff_end = np.random.normal(1, 1)
    tc_end = [persuasion_takeoff_end, coding_takeoff_end]
    
    days = 0
    tc_cur = tc_0

    while True:
        if is_takeoff_over(tc_cur, tc_end):
            break
        tc_cur = capability_increase_step(tc_cur)
        days += 1
    
    days_taken.append(days)

print(sum(days_taken) / len(days_taken))