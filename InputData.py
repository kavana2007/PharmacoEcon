from enum import Enum
import numpy as np

# simulation settings
POP_SIZE = 30000  # cohort population size
SIM_LENGTH = 100  # length of simulation (years)
ALPHA = 0.05  # significance level for calculating confidence intervals
DISCOUNT = 0.03  # annual discount rate

ANNUAL_PROB_ALL_CAUSE_MORT = 731.9 / 100000
ANNUAL_PROB_STROKE_MORT = 63.3 / 100000
ANNUAL_PROB_CHD_MORT = 94.7 / 100000
ANNUAL_PROB_FIRST_STROKE = 0.141
PROB_SURVIVE_FIRST_STROKE = 0.735
PROB_SURVIVE_RECURRENT_STROKE = 0.735
ONE_YEAR_PROB_RECURRENT_STROKE = 0.141 * 0.5  # 50% chance to have a recurrent stroke/chd
STROKE_DURATION = 1 / 52  # 1 week

STROKE_REDUCTION_PER_DOSE = 0.22  # 0.175
ADHERENCE_RATE = 0.75  # 0.4

SIDE_EFFECT_DEATH_INCREASE = 0.01

class HealthStates(Enum):
    """ health states of patients """
    WELL = 0
    STROKE = 1
    POST_STROKE = 2
    STROKE_DEAD = 3
    NATURAL_DEATH = 4

class Dose(Enum):
    """ standard dosage of anti-hypertension drug """
    NONE = 0
    CONSERVATIVE = 1
    INTENSIVE = 2

ANNUAL_STATE_UTILITY = [
    0.77,  # WELL   the side effect of the drug=0.23
    0.154,  # STROKE
    0.693,  # POST-STROKE
    0,  # STROKE DEATH
    0]  # NATURAL DEATH

# annual cost of each health state
ANNUAL_STATE_COST = [
    0,  # WELL
    0,  # STROKE
    8000,  # POST-STROKE
    0,  # STROKE DEATH
    0  # NATURAL DEATH
]

ANNUAL_CONSERVE_COST = 161*12 + 27*4 + 77  # 351*12 + 33*4 + 77
ANNUAL_INTENSE_COST = 231*12 + 27*4 + 77   # 5548*12 + 33*4 + 77

STROKE_COST = 18953
HOSPITALIZATION_COST = 10400


def get_trans_rate_matrix(dose):
    """
    :param dose1: one standard dosage of anti-hypertension drug in all stages
    :param male: gender
    :return: transition rate matrix
    """

    # Part 1: find the annual probability of non-stroke death
    annual_prob_non_stroke_mort = (ANNUAL_PROB_ALL_CAUSE_MORT - ANNUAL_PROB_STROKE_MORT - ANNUAL_PROB_CHD_MORT)
    lambda0 = -np.log(1 - annual_prob_non_stroke_mort)

    # Part 2: lambda 1 + lambda 2
    if dose == Dose.NONE:
        lambda1_plus2 = -np.log(1 - ANNUAL_PROB_FIRST_STROKE)
    elif dose == Dose.CONSERVATIVE:
        lambda1_plus2 = -np.log(1 - ANNUAL_PROB_FIRST_STROKE * (1-STROKE_REDUCTION_PER_DOSE * ADHERENCE_RATE))
    else:
        lambda1_plus2 = -np.log(1 - ANNUAL_PROB_FIRST_STROKE * (1-STROKE_REDUCTION_PER_DOSE*2 * ADHERENCE_RATE))

    # Part 3
    lambda1 = lambda1_plus2 * PROB_SURVIVE_FIRST_STROKE
    lambda2 = lambda1_plus2 * (1 - PROB_SURVIVE_FIRST_STROKE)

    # Part 4
    if dose == Dose.NONE:
        lambda3_plus4 = -1 / np.log(1 - ONE_YEAR_PROB_RECURRENT_STROKE)
    elif dose == Dose.CONSERVATIVE:
        lambda3_plus4 = -1 / np.log(
            1 - ONE_YEAR_PROB_RECURRENT_STROKE * STROKE_REDUCTION_PER_DOSE * ADHERENCE_RATE)
    else:
        lambda3_plus4 = -1 / np.log(
            1 - ONE_YEAR_PROB_RECURRENT_STROKE * STROKE_REDUCTION_PER_DOSE**2 * ADHERENCE_RATE)

    # Part 5
    lambda3 = lambda3_plus4 * PROB_SURVIVE_RECURRENT_STROKE
    lambda4 = lambda3_plus4 * (1 - PROB_SURVIVE_RECURRENT_STROKE)

    # Part 6
    lambda5 = 1 / STROKE_DURATION

    # find multipliers to adjust the rates depending on whether the patient
    # is receiving conservative treatment or intensive treatment
    if dose == Dose.NONE:
        r1 = 1
        r2 = 1
    elif dose == Dose.CONSERVATIVE:
        r1 = 1 - STROKE_REDUCTION_PER_DOSE * ADHERENCE_RATE
        r2 = 1 + SIDE_EFFECT_DEATH_INCREASE
    else:
        r1 = 1 - STROKE_REDUCTION_PER_DOSE * 2 * ADHERENCE_RATE
        r2 = 1 + 2 * SIDE_EFFECT_DEATH_INCREASE

    rate_matrix = [
        [0, lambda1, 0, lambda2, lambda0],  # WELL
        [0, 0, lambda5, 0, 0],  # STROKE
        [0, lambda3 * r1, 0, lambda4 * r1, lambda0 * r2],  # POST-STROKE
        [0, 0, 0, 0, 0],  # STROKE-DEATH
        [0, 0, 0, 0, 0]  # NATURAL-DEATH
    ]

    return rate_matrix

print('Transition rate matrix without treatment:')
print(get_trans_rate_matrix(dose=Dose.NONE))

print('Transition rate matrix with conservative treatment:')
print(get_trans_rate_matrix(dose=Dose.CONSERVATIVE))

print('Transition rate matrix with intensive treatment:')
print(get_trans_rate_matrix(dose=Dose.INTENSIVE))
