'''
Copyright 2022 Airbus SAS
Modifications on 2023/06/14-2023/11/02 Copyright 2023 Capgemini

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from climateeconomics.core.core_witness.climateeco_discipline import ClimateEcoDiscipline
from climateeconomics.glossarycore import GlossaryCore
from sostrades_core.tools.post_processing.charts.chart_filter import ChartFilter
from climateeconomics.core.core_sectorization.macroeconomics_sectorization_model import MacroeconomicsModel
from climateeconomics.sos_wrapping.sos_wrapping_sectors.agriculture.agriculture_discipline import AgricultureDiscipline
from climateeconomics.sos_wrapping.sos_wrapping_sectors.services.services_discipline import ServicesDiscipline
from climateeconomics.sos_wrapping.sos_wrapping_sectors.industrial.industrial_discipline import IndustrialDiscipline
from sostrades_core.tools.post_processing.charts.two_axes_instanciated_chart import InstanciatedSeries, \
    TwoAxesInstanciatedChart
import numpy as np
import pandas as pd
from copy import deepcopy


class MacroeconomicsDiscipline(ClimateEcoDiscipline):
    ''' Discipline intended to agregate resource parameters'''

    # ontology information
    _ontology_data = {
        'label': 'Macroeconomics Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fa-solid fa-city',
        'version': '',
    }

    DESC_IN = {
        GlossaryCore.InvestmentDfValue: GlossaryCore.InvestmentDf,
        GlossaryCore.SectorListValue: GlossaryCore.SectorList,
    }

    DESC_OUT = {
        GlossaryCore.EconomicsDfValue: GlossaryCore.SectorizedEconomicsDf,
        GlossaryCore.EconomicsDetailDfValue: GlossaryCore.SectorizedEconomicsDetailDf,
    }

    def init_execution(self):
        inputs_dict = self.get_sosdisc_inputs()
        self.macro_model = MacroeconomicsModel(inputs_dict)

    def setup_sos_disciplines(self):
        dynamic_inputs = {}

        if GlossaryCore.SectorListValue in self.get_data_in():
            sector_list = self.get_sosdisc_inputs(GlossaryCore.SectorListValue)

            for sector in sector_list:
                capital_df_disc = GlossaryCore.get_dynamic_variable(GlossaryCore.CapitalDf)
                capital_df_disc[self.NAMESPACE] = GlossaryCore.NS_MACRO
                dynamic_inputs[f'{sector}.{GlossaryCore.CapitalDfValue}'] = capital_df_disc
                dynamic_inputs[f'{sector}.{GlossaryCore.ProductionDfValue}'] = GlossaryCore.get_dynamic_variable(GlossaryCore.ProductionDf)

            self.add_inputs(dynamic_inputs)

    def run(self):
        """run method"""
        inputs_dict = self.get_sosdisc_inputs()
        self.macro_model.compute(inputs_dict)

        outputs_dict = {
            GlossaryCore.EconomicsDfValue: self.macro_model.economics_df,
            GlossaryCore.EconomicsDetailDfValue: self.macro_model.economics_detail_df
        }

        self.store_sos_outputs_values(outputs_dict)

    def compute_sos_jacobian(self):
        """
        Compute jacobian for each coupling variable
        gradient of coupling variable to compute:
        net_output and invest wrt sector net_output 
        """
        sector_list = self.get_sosdisc_inputs(GlossaryCore.SectorListValue)

        # Gradient wrt each sector production df: same for all sectors
        grad_netoutput = self.macro_model.get_derivative_sectors()
        for sector in sector_list:
            self.set_partial_derivative_for_other_types((GlossaryCore.EconomicsDfValue, GlossaryCore.GrossOutput),
                                                        (f'{sector}.{GlossaryCore.ProductionDfValue}',
                                                         GlossaryCore.GrossOutput),
                                                        grad_netoutput)
            self.set_partial_derivative_for_other_types((GlossaryCore.EconomicsDfValue, GlossaryCore.OutputNetOfDamage),
                                                        (f'{sector}.{GlossaryCore.ProductionDfValue}', GlossaryCore.OutputNetOfDamage),
                                                        grad_netoutput)
            self.set_partial_derivative_for_other_types((GlossaryCore.EconomicsDfValue, GlossaryCore.Capital),
                                                        (f'{sector}.{GlossaryCore.CapitalDfValue}', GlossaryCore.Capital), grad_netoutput)

    def get_chart_filter_list(self):

        chart_filters = []

        chart_list = [GlossaryCore.GrossOutput,
                      GlossaryCore.OutputNetOfDamage,
                      GlossaryCore.Capital,
                      'share capital',
                      'share output',
                      'output growth']

        chart_filters.append(ChartFilter(
            'Charts filter', chart_list, chart_list, 'charts'))

        return chart_filters

    def get_post_processing_list(self, chart_filters=None):

        instanciated_charts = []

        # Overload default value with chart filter
        if chart_filters is not None:
            for chart_filter in chart_filters:
                if chart_filter.filter_key == 'charts':
                    chart_list = chart_filter.selected_values

        economics_df = deepcopy(self.get_sosdisc_outputs(GlossaryCore.EconomicsDetailDfValue))
        investment_df = deepcopy(self.get_sosdisc_inputs(GlossaryCore.InvestmentDfValue))
        sector_list = self.get_sosdisc_inputs(GlossaryCore.SectorListValue)

        # Overload default value with chart filter
        if chart_filters is not None:
            for chart_filter in chart_filters:
                if chart_filter.filter_key == 'charts':
                    chart_list = chart_filter.selected_values

        if GlossaryCore.GrossOutput in chart_list:

            years = list(economics_df.index)
            chart_name = 'Breakdown of gross output'
            new_chart = TwoAxesInstanciatedChart(GlossaryCore.Years, 'world output [trillion $2020]',
                                                 chart_name=chart_name, stacked_bar=True)

            new_series = InstanciatedSeries(
                years, list(investment_df[GlossaryCore.InvestmentsValue]),'Investments', 'bar', True)
            new_chart.series.append(new_series)

            new_series = InstanciatedSeries(
                years, list(economics_df[GlossaryCore.Consumption]), 'Consumption', 'bar', True)
            new_chart.series.append(new_series)

            new_series = InstanciatedSeries(
                years, list(economics_df[GlossaryCore.Damages]), 'Damages', 'bar', True)
            new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        if GlossaryCore.OutputNetOfDamage in chart_list:
            chart_name = 'Global Output net of damage breakdown by sector'
            new_chart = TwoAxesInstanciatedChart(GlossaryCore.Years, 'T$', stacked_bar=True,
                                                 chart_name=chart_name)

            for sector in sector_list:
                production_df = self.get_sosdisc_inputs(f'{sector}.{GlossaryCore.ProductionDfValue}')
                sector_net_output = list(production_df[GlossaryCore.OutputNetOfDamage].values)

                new_series = InstanciatedSeries(years, sector_net_output,
                                                sector, 'bar', True)
                new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)


        if GlossaryCore.Capital in chart_list:

            to_plot = [GlossaryCore.Capital, GlossaryCore.UsableCapital]
            legend = {GlossaryCore.Capital: 'capital stock',
                      GlossaryCore.UsableCapital: 'usable capital stock'}
            years = list(economics_df.index)

            chart_name = 'Total capital stock and usable capital'
            new_chart = TwoAxesInstanciatedChart(GlossaryCore.Years, 'capital stock [T$]',
                                                 chart_name=chart_name)

            for key in to_plot:
                ordonate_data = list(economics_df[key])
                new_series = InstanciatedSeries(
                    years, ordonate_data, legend[key], 'lines', True)
                new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        if 'share capital' in chart_list:
            capital = economics_df[GlossaryCore.Capital].values
            chart_name = 'Capital distribution between economic sectors'
            new_chart = TwoAxesInstanciatedChart(GlossaryCore.Years, 'share of total capital stock [%]', stacked_bar=True,
                                                 chart_name=chart_name)

            for sector in sector_list:
                capital_df = self.get_sosdisc_inputs(f'{sector}.{GlossaryCore.CapitalDfValue}')
                sector_capital = capital_df[GlossaryCore.Capital].values
                share = (sector_capital / capital) * 100
                ordonate_data = list(share)
                new_series = InstanciatedSeries(years, ordonate_data,
                                                sector, 'bar', True)
                new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        if 'share output' in chart_list:
            output = economics_df[GlossaryCore.OutputNetOfDamage].values
            chart_name = 'Sectors share of total economics net output'
            new_chart = TwoAxesInstanciatedChart(GlossaryCore.Years, 'share of total net output [%]', stacked_bar=True,
                                                 chart_name=chart_name)

            for sector in sector_list:
                production_df = self.get_sosdisc_inputs(f'{sector}.{GlossaryCore.ProductionDfValue}')
                sector_output = production_df[GlossaryCore.OutputNetOfDamage].values
                share = (sector_output / output) * 100
                ordonate_data = list(share)
                new_series = InstanciatedSeries(years, ordonate_data,
                                                sector, 'bar', True)
                new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        if 'output growth' in chart_list:

            to_plot = [GlossaryCore.OutputGrowth]
            years = list(economics_df.index)
            chart_name = 'Net output growth rate over years'
            new_chart = TwoAxesInstanciatedChart(GlossaryCore.Years, ' growth rate [-]',
                                                 chart_name=chart_name)
            for key in to_plot:
                ordonate_data = list(economics_df[key])
                new_series = InstanciatedSeries(
                    years, ordonate_data, key, 'lines', True)
                new_chart.series.append(new_series)

            instanciated_charts.append(new_chart)

        return instanciated_charts
