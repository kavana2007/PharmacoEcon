from enum import Enum
import InputData as D


class HealthStates(Enum):
    """ health states of patients """
    WELL = 0
    STROKE = 1
    POST_STROKE = 2
    STROKE_DEAD = 3
    NATURAL_DEATH = 4


class Therapies(Enum):
    """ intensive vs conservative """
    NONE = 0
    CONSERVATIVE = 1
    INTENSIVE = 2

class ParametersFixed:
    def __init__(self, therapy):

        # selected therapy
        self.therapy = therapy

        # initial health state
        self.initialHealthState = HealthStates.WELL

        # transition probability matrix of the selected therapy
        self.rateMatrix = []

        # calculate transition rate matrices depending of which therapy options is in use
        if therapy == Therapies.NONE:
            self.rateMatrix = D.get_trans_rate_matrix(dose = D.Dose.NONE)
        elif therapy == Therapies.INTENSIVE:
            self.rateMatrix = D.get_trans_rate_matrix(dose = D.Dose.INTENSIVE)
        else:
            self.rateMatrix = D.get_trans_rate_matrix(dose = D.Dose.CONSERVATIVE)

        # annual treatment cost
        if self.therapy == Therapies.NONE:
            self.annualDrugCost = 0
        elif self.therapy == Therapies.INTENSIVE:
            self.annualDrugCost = D.ANNUAL_INTENSE_COST
        elif self.therapy == Therapies.CONSERVATIVE:
            self.annualDrugCost = D.ANNUAL_CONSERVE_COST

        # stroke cost
        self.strokeCost = D.STROKE_COST

        # hospitalization cost
        self.hospitalCost = D.HOSPITALIZATION_COST

        # state costs and utilities
        self.annualStateCosts = D.ANNUAL_STATE_COST
        self.annualStateUtilities = D.ANNUAL_STATE_UTILITY

        # discount rate
        self.discountRate = D.DISCOUNT

