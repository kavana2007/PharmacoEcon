from InputData import HealthStates
import SimPy.RandomVariantGenerators as RVGs
import SimPy.MarkovClasses as Markov
import SimPy.SamplePathClasses as Path
import SimPy.EconEval as Econ
import SimPy.StatisticalClasses as Stat


class Patient:
    def __init__(self, id, parameters):

        self.id = id
        self.params = parameters
        self.stateMonitor = PatientStateMonitor(parameters=parameters)

    def simulate(self, sim_length):

        # random number generator for this patient
        rng = RVGs.RNG(seed=self.id)
        # gillespie algorithm
        gillespie = Markov.Gillespie(transition_rate_matrix=self.params.rateMatrix)

        t = 0  # simulation time
        if_stop = False

        while not if_stop:

            # find time until next event (dt), and next state
            # (note that the gillespie algorithm returns None for dt if the process
            # is in an absorbing state)
            dt, new_state_index = gillespie.get_next_state(
                current_state_index=self.stateMonitor.currentState.value,
                rng=rng)

            # stop if time to next event (dt) is None
            if dt is None:
                if_stop = True

            # else if  the next event occurs beyond simulation length
            elif dt + t > sim_length:
                if_stop = True
                # collect cost and health outcomes up to the simulation length
                self.stateMonitor.costUtilityMonitor.update(time=sim_length,
                                                            current_state=self.stateMonitor.currentState,
                                                            next_state=self.stateMonitor.currentState)
            else:
                # advance time to the time of next event
                t += dt
                # update health state
                self.stateMonitor.update(time=t, new_state=HealthStates(new_state_index))


class PatientStateMonitor:
    def __init__(self, parameters):

        self.currentState = parameters.initialHealthState    # assuming everyone starts in "Well"
        self.survivalTime = None
        self.nStrokes = 0
        self.costUtilityMonitor = PatientCostUtilityMonitor(parameters=parameters)

    def update(self, time, new_state):

        if new_state in (HealthStates.STROKE_DEAD, HealthStates.NATURAL_DEATH):
            self.survivalTime = time

        if new_state == HealthStates.STROKE:
            self.nStrokes += 1

        self.costUtilityMonitor.update(time=time,
                                       current_state=self.currentState,
                                       next_state=new_state)

        self.currentState = new_state

    def get_if_alive(self):
        if self.currentState in (HealthStates.STROKE_DEAD, HealthStates.NATURAL_DEATH):
            return False
        else:
            return True


class PatientCostUtilityMonitor:
    def __init__(self, parameters):

        self.tLastRecorded = 0  # time when the last cost and outcomes got recorded

        self.params = parameters
        self.totalDiscountedCost = 0
        self.totalDiscountedUtility = 0

    def update(self, time, current_state, next_state):

        # cost (per unit of time) during the period since the last recording until now
        cost = self.params.annualStateCosts[current_state.value] + self.params.annualDrugCost

        # discounted cost and utility (continuously compounded)
        discounted_cost = Econ.pv_continuous_payment(payment=cost,
                                                     discount_rate=self.params.discountRate,
                                                     discount_period=(self.tLastRecorded, time))

        # add discounted stoke cost, if stroke occurred
        if next_state == HealthStates.STROKE_DEAD:
            discounted_cost += Econ.pv_single_payment(payment=self.params.strokeCost + self.params.hospitalCost,
                                                      discount_rate=self.params.discountRate,
                                                      discount_period=time,
                                                      discount_continuously=True)

        # utility (per unit of time) during the period since the last recording until now
        utility = self.params.annualStateUtilities[current_state.value]
        discounted_utility = Econ.pv_continuous_payment(payment=utility,
                                                        discount_rate=self.params.discountRate,
                                                        discount_period=(self.tLastRecorded, time))

        # update total discounted cost and utility
        self.totalDiscountedCost += discounted_cost
        self.totalDiscountedUtility += discounted_utility

        # update the time since last recording to the current time
        self.tLastRecorded = time


class Cohort:
    def __init__(self, id, pop_size, parameters):
        """ create a cohort of patients
        :param id: cohort ID
        :param pop_size: population size of this cohort
        :param parameters: parameters
        """
        self.id = id
        self.popSize = pop_size
        self.params = parameters
        self.cohortOutcomes = CohortOutcomes()  # outcomes of the this simulated cohort

    def simulate(self, sim_length):
        """ simulate the cohort of patients over the specified number of time-steps
        :param sim_length: simulation length
        """

        # populate the cohort
        patients = []
        for i in range(self.popSize):
            # create a new patient (use id * pop_size + n as patient id)
            patient = Patient(id=self.id * self.popSize + i, parameters=self.params)
            # add the patient to the cohort
            patients.append(patient)

        # simulate all patients
        for patient in patients:
            # simulate
            patient.simulate(sim_length)

        # store outputs of this simulation
        self.cohortOutcomes.extract_outcomes(patients)


class CohortOutcomes:
    def __init__(self):

        self.survivalTimes = []
        self.nTotalStrokes = []
        self.nLivingPatients = None
        self.costs = []
        self.utilities = []

        self.statSurvivalTime = None
        self.statNumStrokes = None
        self.statCost = None
        self.statUtility = None

    def extract_outcomes(self, simulated_patients):

        for patient in simulated_patients:
            if not (patient.stateMonitor.survivalTime is None):
                self.survivalTimes.append(patient.stateMonitor.survivalTime)
            self.nTotalStrokes.append(patient.stateMonitor.nStrokes)
            self.costs.append(patient.stateMonitor.costUtilityMonitor.totalDiscountedCost)
            self.utilities.append(patient.stateMonitor.costUtilityMonitor.totalDiscountedUtility)

        self.statNumStrokes = Stat.SummaryStat('Number of strokes',self.nTotalStrokes)
        self.statSurvivalTime = Stat.SummaryStat('Survival Time',self.survivalTimes)
        self.statCost = Stat.SummaryStat('Discounted Cost',self.costs)
        self.statUtility = Stat.SummaryStat('Discounted Utility',self.utilities)

        self.nLivingPatients = Path.PrevalencePathBatchUpdate(
            name='# of living patients',
            initial_size=len(simulated_patients),
            times_of_changes=self.survivalTimes,
            increments=[-1]*len(self.survivalTimes)
        )
