import os
import numpy as np
import pandas as pd
import chaospy as cp
from easyvvuq import OutputType
from .base import BaseAnalysisElement

# author: Jalal Lakhlili
__license__ = "LGPL"

# TODO:
# 2. Add pd.read_hdf (https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-hdf5).
# 3. Add VERBOSE argument (False by default) to allow the user to store output_file or no.
# 4. Test cp.fit_regression to approximate solver.
# 5. Organize and add more results (Sobols 2nd order, Percentiles, ...).


class PCEAnalysis(BaseAnalysisElement):
    def element_name(self):
        return "PCE_Analysis"

    def element_version(self):
        return "0.1"

    def __init__(self, data_src, params_cols=[],
                 value_cols=[], *args, **kwargs):

        # TODO: Fix this to allow more flexibility - basically pass through
        # available options to `pd.DataFrame.describe()`

        # Handles creation of `self.data_src` attribute (dict)
        super().__init__(data_src, *args, **kwargs)

        data_src = self.data_src
        if data_src:
            if 'files' in data_src:
                if len(data_src['files']) != 1:
                    raise RuntimeError(
                        "Data source must contain a SINGLE file path for this UQP")
                else:
                    self.data_frame = pd.read_csv(
                        data_src['files'][0], sep='\t')

        self.value_cols = value_cols
        if self.campaign is not None:
            if not params_cols:
                self.params_cols = list(self.campaign.params_info.keys())
            self.value_cols = self.campaign.decoder.output_columns
        else:
            self.params_cols = params_cols
        self.output_type = OutputType.SUMMARY

    def _apply_analysis(self):

        if self.data_frame is None:
            raise RuntimeError("UQP needs a data frame to analyse")

        df = self.data_frame

        # output_dir  = self.output_dir
        # output_file = os.path.join(output_dir, 'pce_basic_stats.tsv')

        # Get the Polynomial
        P = self.campaign.P

        # Compute nodes and weights
        nodes, weights = cp.generate_quadrature(order=self.campaign.quad_order,
                                                domain=self.campaign.distribution,
                                                rule=self.campaign.quad_rule,
                                                sparse=self.campaign.quad_sparse)

        # Extract output values for each quantity of interest from Dataframe
        samples = {k: [] for k in self.value_cols}
        for i in range(self.campaign.run_number):
            for k in self.value_cols:
                values = df.loc[df['run_id'] == 'Run_' + str(i)][k].to_numpy()
                samples[k].append(values)

        # Perform analysis for each quantity of interest
        statistical_moments = {}
        sobol_first = {}
        correlation_matrix = {}
        for k in self.value_cols:
            # Approximation solver
            fit = cp.fit_quadrature(P, nodes, weights, samples[k])

            # Statistical moments
            mean = cp.E(fit, self.campaign.distribution)
            var = cp.Var(fit, self.campaign.distribution)
            std = cp.Std(fit, self.campaign.distribution)
            statistical_moments[k] = pd.DataFrame(
                {'mean': mean, 'var': var, 'std': std})

            # Correlation matrix
            correlation_matrix[k] = cp.Corr(fit, self.campaign.distribution)

            # First Sobol indices
            sobol_first_narr = cp.Sens_m(fit, self.campaign.distribution)
            sobol_first_dict = {}
            i_par = 0
            for param_name in self.campaign.vars.keys():
                sobol_first_dict[param_name] = sobol_first_narr[i_par]
                i_par += 1
            sobol_first[k] = pd.DataFrame(sobol_first_dict)

        return statistical_moments, correlation_matrix, sobol_first
