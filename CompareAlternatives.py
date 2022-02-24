import InputData as D
import ParameterClasses as P
import MarkovClasses as Cls
import Support as Support

# simulating no therapy
# create a cohort
cohort_none = Cls.Cohort(id=2,
                         pop_size=D.POP_SIZE,
                         parameters=P.ParametersFixed(therapy=P.Therapies.NONE))
# simulate the cohort
cohort_none.simulate(sim_length=D.SIM_LENGTH)

# simulating conservative anti-hypertension therapy
# create a cohort
cohort_conserve = Cls.Cohort(id=2017,
                             pop_size=D.POP_SIZE,
                             parameters=P.ParametersFixed(therapy=P.Therapies.CONSERVATIVE))
# simulate the cohort
cohort_conserve.simulate(sim_length=D.SIM_LENGTH)

# simulating intensive anti-hypertension therapy
# create a cohort
cohort_intense = Cls.Cohort(id=2018,
                            pop_size=D.POP_SIZE,
                            parameters=P.ParametersFixed(therapy=P.Therapies.INTENSIVE))
# simulate the cohort
cohort_intense.simulate(sim_length=D.SIM_LENGTH)


# print the estimates for the mean survival time and mean time to stroke
Support.print_outcomes(sim_outcomes=cohort_none.cohortOutcomes,
                       therapy_name=P.Therapies.NONE)

Support.print_outcomes(sim_outcomes=cohort_conserve.cohortOutcomes,
                       therapy_name=P.Therapies.CONSERVATIVE)

Support.print_outcomes(sim_outcomes=cohort_intense.cohortOutcomes,
                       therapy_name=P.Therapies.INTENSIVE)

# plot survival curves and histograms
Support.plot_survival_curves_and_histograms(sim_outcomes_none=cohort_none.cohortOutcomes,
                                            sim_outcomes_mono=cohort_conserve.cohortOutcomes,
                                            sim_outcomes_combo=cohort_intense.cohortOutcomes)

# print comparative outcomes
Support.print_comparative_outcomes(sim_outcomes_none=cohort_conserve.cohortOutcomes,
                                   sim_outcomes_anti=cohort_intense.cohortOutcomes)

# report the CEA results
Support.report_CEA_CBA(sim_outcomes_none=cohort_conserve.cohortOutcomes,
                       sim_outcomes_anti=cohort_intense.cohortOutcomes)
