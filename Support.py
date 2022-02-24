import InputData as D
import SimPy.Plots.SamplePaths as Path
import SimPy.Plots.Histogram as Hist
import SimPy.StatisticalClasses as Stat
import SimPy.EconEval as Econ


def print_outcomes(sim_outcomes, therapy_name):
    """ prints the outcomes of a simulated cohort
    :param sim_outcomes: outcomes of a simulated cohort
    :param therapy_name: the name of the selected therapy
    """
    # mean and confidence interval of patient survival time
    survival_mean_CI_text = sim_outcomes.statSurvivalTime\
        .get_formatted_mean_and_interval(interval_type='c',
                                         alpha=D.ALPHA,
                                         deci=2)

    # mean and confidence interval text of time to AIDS
    num_strokes_CI_text = sim_outcomes.statNumStrokes\
        .get_formatted_mean_and_interval(interval_type='c',
                                         alpha=D.ALPHA,
                                         deci=2)

    # mean and confidence interval text of discounted total cost
    cost_mean_CI_text = sim_outcomes.statCost\
        .get_formatted_mean_and_interval(interval_type='c',
                                         alpha=D.ALPHA,
                                         deci=0,
                                         form=',')

    # mean and confidence interval text of discounted total utility
    utility_mean_CI_text = sim_outcomes.statUtility\
        .get_formatted_mean_and_interval(interval_type='c',
                                         alpha=D.ALPHA,
                                         deci=2)

    # print outcomes
    print(therapy_name)
    print("  Estimate of mean survival time and {:.{prec}%} confidence interval:".format(1 - D.ALPHA, prec=0),
          survival_mean_CI_text)
    print("  Estimate of number of strokes and {:.{prec}%} confidence interval:".format(1 - D.ALPHA, prec=0),
          num_strokes_CI_text)
    print("  Estimate of discounted cost and {:.{prec}%} confidence interval:".format(1 - D.ALPHA, prec=0),
          cost_mean_CI_text)
    print("  Estimate of discounted utility and {:.{prec}%} confidence interval:".format(1 - D.ALPHA, prec=0),
          utility_mean_CI_text)
    print("")


def plot_survival_curves_and_histograms(sim_outcomes_none, sim_outcomes_mono, sim_outcomes_combo):
    """ draws the survival curves and the histograms of time until deaths
    :param sim_outcomes_none: outcomes of a cohort simulated without treatment
    :param sim_outcomes_mono: outcomes of a cohort simulated under conservative treatment
    :param sim_outcomes_combo: outcomes of a cohort simulated under intensive treatment
    """

    # get survival curves of both treatments
    survival_curves = [
        sim_outcomes_none.nLivingPatients,
        sim_outcomes_mono.nLivingPatients,
        sim_outcomes_combo.nLivingPatients
    ]

    # graph survival curve
    Path.plot_sample_paths(
        sample_paths=survival_curves,
        title='Survival curve',
        x_label='Simulation time step (year)',
        y_label='Number of alive patients',
        legends=['None treatment','Conservative treatment', 'Intensive treatment'],
        color_codes=['orange', 'green', 'blue']
    )

    # histograms of survival times
    set_of_strokes = [
        sim_outcomes_none.nTotalStrokes,
        sim_outcomes_mono.nTotalStrokes,
        sim_outcomes_combo.nTotalStrokes
    ]

    # graph histograms
    Hist.plot_histograms(
        data_sets=set_of_strokes,
        title='Histogram of Patient CVD Events Number',
        x_label='Number of CVD Events',
        y_label='Counts',
        bin_width=1,
        legends=['None treatment', 'Conservative treatment', 'Intensive treatment'],
        color_codes=['orange', 'green', 'blue'],
        transparency=0.5
    )


def print_comparative_outcomes(sim_outcomes_none, sim_outcomes_anti):
    """ prints average increase in survival time, discounted cost, and discounted utility
    under combination therapy compared to mono therapy
    :param sim_outcomes_none: outcomes of a cohort simulated under conservative treatment
    :param sim_outcomes_anti: outcomes of a cohort simulated under intensive treatment
    """

    # increase in mean survival time under combination therapy with respect to mono therapy
    increase_survival_time = Stat.DifferenceStatIndp(
        name='Increase in mean survival time',
        x=sim_outcomes_anti.survivalTimes,
        y_ref=sim_outcomes_none.survivalTimes)

    # estimate and CI
    estimate_CI = increase_survival_time.get_formatted_mean_and_interval(interval_type='c',
                                                                         alpha=D.ALPHA,
                                                                         deci=2)
    print("Increase in mean survival time and {:.{prec}%} confidence interval:"
          .format(1 - D.ALPHA, prec=0),
          estimate_CI)

    # increase in mean discounted cost under combination therapy with respect to mono therapy
    increase_discounted_cost = Stat.DifferenceStatIndp(
        name='Increase in mean discounted cost',
        x=sim_outcomes_anti.costs,
        y_ref=sim_outcomes_none.costs)

    # estimate and CI
    estimate_CI = increase_discounted_cost.get_formatted_mean_and_interval(interval_type='c',
                                                                           alpha=D.ALPHA,
                                                                           deci=2,
                                                                           form=',')
    print("Increase in mean discounted cost and {:.{prec}%} confidence interval:"
          .format(1 - D.ALPHA, prec=0),
          estimate_CI)

    # increase in mean discounted utility under combination therapy with respect to mono therapy
    increase_discounted_utility = Stat.DifferenceStatIndp(
        name='Increase in mean discounted utility',
        x=sim_outcomes_anti.utilities,
        y_ref=sim_outcomes_none.utilities)

    # estimate and CI
    estimate_CI = increase_discounted_utility.get_formatted_mean_and_interval(interval_type='c',
                                                                              alpha=D.ALPHA,
                                                                              deci=2)
    print("Increase in mean discounted utility and {:.{prec}%} confidence interval:"
          .format(1 - D.ALPHA, prec=0),
          estimate_CI)

    # increase in mean discounted utility under combination therapy with respect to mono therapy
    increase_num_strokes = Stat.DifferenceStatIndp(
        name='Increase in mean discounted utility',
        x=sim_outcomes_anti.nTotalStrokes,
        y_ref=sim_outcomes_none.nTotalStrokes)

    # estimate and CI
    estimate_CI = increase_num_strokes.get_formatted_mean_and_interval(interval_type='c',
                                                                              alpha=D.ALPHA,
                                                                              deci=2)
    print("Increase in number of CVD events and {:.{prec}%} confidence interval:"
          .format(1 - D.ALPHA, prec=0),
          estimate_CI)


def report_CEA_CBA(sim_outcomes_none, sim_outcomes_anti):
    """ performs cost-effectiveness and cost-benefit analyses
    :param sim_outcomes_mono: outcomes of a cohort simulated under mono therapy
    :param sim_outcomes_combo: outcomes of a cohort simulated under combination therapy
    """

    # define two strategies
    no_therapy_strategy = Econ.Strategy(
        name='Conservative treatment',
        cost_obs=sim_outcomes_none.costs,
        effect_obs=sim_outcomes_none.utilities,
        color='green'
    )
    anti_therapy_strategy = Econ.Strategy(
        name='Intensive treatment',
        cost_obs=sim_outcomes_anti.costs,
        effect_obs=sim_outcomes_anti.utilities,
        color='blue'
    )

    # do CEA
    CEA = Econ.CEA(
        strategies=[no_therapy_strategy, anti_therapy_strategy],
        if_paired=False
    )

    # plot cost-effectiveness figure
    CEA.plot_CE_plane(
        title='Cost-Effectiveness Analysis',
        x_label='Additional QALYs',
        y_label='Additional Cost'
    )

    # report the CE table
    CEA.build_CE_table(
        interval_type='c',
        alpha=D.ALPHA,
        cost_digits=0,
        effect_digits=2,
        icer_digits=2,
        file_name='CETable.csv')

    # CBA
    NBA = Econ.CBA(
        strategies=[no_therapy_strategy, anti_therapy_strategy],
        wtp_range=[0, 200000],
        if_paired=False
    )
    # show the net monetary benefit figure
    NBA.plot_incremental_nmbs(
        title='Cost-Benefit Analysis',
        x_label='Willingness-to-pay per QALY ($)',
        y_label='Incremental Net Monetary Benefit ($)',
        interval_type='c',
        show_legend=True,
        figure_size=(6, 5)
    )


