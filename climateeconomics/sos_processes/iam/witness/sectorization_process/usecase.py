'''
Copyright 2022 Airbus SAS
Modifications on 2023/04/19-2023/11/22 Copyright 2023 Capgemini

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
from os.path import join, dirname

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from climateeconomics.database.database_witness_core import DatabaseWitnessCore
from climateeconomics.glossarycore import GlossaryCore
from sostrades_core.study_manager.study_manager import StudyManager


def update_dspace_with(dspace_dict, name, value, lower, upper):
    ''' type(value) has to be ndarray
    '''
    if not isinstance(lower, (list, np.ndarray)):
        lower = [lower] * len(value)
    if not isinstance(upper, (list, np.ndarray)):
        upper = [upper] * len(value)
    dspace_dict['variable'].append(name)
    dspace_dict['value'].append(value.tolist())
    dspace_dict['lower_bnd'].append(lower)
    dspace_dict['upper_bnd'].append(upper)
    dspace_dict['dspace_size'] += len(value)


def update_dspace_dict_with(dspace_dict, name, value, lower, upper, activated_elem=None, enable_variable=True):
    if not isinstance(lower, (list, np.ndarray)):
        lower = [lower] * len(value)
    if not isinstance(upper, (list, np.ndarray)):
        upper = [upper] * len(value)

    if activated_elem is None:
        activated_elem = [True] * len(value)
    dspace_dict[name] = {'value': value,
                         'lower_bnd': lower, 'upper_bnd': upper, 'enable_variable': enable_variable,
                         'activated_elem': activated_elem}

    dspace_dict['dspace_size'] += len(value)


class Study(StudyManager):

    def __init__(self, year_start=GlossaryCore.YearStartDefault, year_end=GlossaryCore.YearEndDefault, time_step=1, name='', execution_engine=None,
                 main_study: bool=True):
        super().__init__(__file__, execution_engine=execution_engine)
        self.main_study = main_study
        self.study_name = 'usecase'
        self.macro_name = 'Macroeconomics'
        self.labormarket_name = 'LaborMarket'
        self.redistrib_energy_name = 'SectorsEnergyDistribution'
        self.year_start = year_start
        self.year_end = year_end
        self.time_step = time_step
        self.nb_poles = 8

    def setup_usecase(self, study_folder_path=None):
        setup_data_list = []

        years = np.arange(self.year_start, self.year_end + 1, 1)
        self.nb_per = round(self.year_end - self.year_start + 1)


        # Damage
        damage_fraction_df = pd.DataFrame(
            {GlossaryCore.Years: years,
             GlossaryCore.DamageFractionOutput: np.zeros(self.nb_per),
             GlossaryCore.BaseCarbonPrice: np.zeros(self.nb_per)})


        # economisc df to init mda
        gdp = [130.187] * len(years)
        economics_df = pd.DataFrame({GlossaryCore.Years: years, GlossaryCore.OutputNetOfDamage: gdp})

        #Investment
        invest_indus_start = DatabaseWitnessCore.InvestInduspercofgdp2020.value
        invest_agri_start = DatabaseWitnessCore.InvestAgriculturepercofgdp2020.value
        invest_services_start = DatabaseWitnessCore.InvestServicespercofgdp2020.value
        invest_energy_start = 1.077
        total_invest_start = invest_indus_start + invest_agri_start + invest_services_start + invest_energy_start

        total_invests = pd.DataFrame(
            {GlossaryCore.Years: years,
             GlossaryCore.InvestmentsValue: total_invest_start})



       #Energy
        energy_investment_wo_tax = pd.DataFrame({GlossaryCore.Years: years,
                                                 GlossaryCore.EnergyInvestmentsWoTaxValue: 1000.
                                                 })

        global_data_dir = join(dirname(dirname(dirname(dirname(dirname(__file__))))), 'data')
        weighted_average_percentage_per_sector_df = pd.read_csv(
            join(global_data_dir, 'weighted_average_percentage_per_sector.csv'))
        subsector_share_dict = {
            **{GlossaryCore.Years: np.arange(self.year_start, self.year_end + 1), },
            **dict(zip(weighted_average_percentage_per_sector_df.columns[1:],
                       weighted_average_percentage_per_sector_df.values[0, 1:]))
        }
        gdp_section_df = pd.DataFrame(subsector_share_dict)

        cons_input = {
            f"{self.study_name}.{GlossaryCore.YearStart}": self.year_start,
            f"{self.study_name}.{GlossaryCore.YearEnd}": self.year_end,
            f"{self.study_name}.{self.macro_name}.{GlossaryCore.InvestmentDfValue}": total_invests,
            f"{self.study_name}.{GlossaryCore.DamageFractionDfValue}": damage_fraction_df,
            f"{self.study_name}.{GlossaryCore.EconomicsDfValue}": economics_df,
            f"{self.study_name}.{GlossaryCore.EnergyInvestmentsWoTaxValue}": energy_investment_wo_tax,
            f'{self.study_name}.{GlossaryCore.SectionGdpPercentageDfValue}': gdp_section_df,
        }

        if self.main_study:
            gdp_forecast = DatabaseWitnessCore.WorldGDPForecastSSP3.value[GlossaryCore.GrossOutput].values
            population_2021 = DatabaseWitnessCore.WorldPopulationForecast.value[GlossaryCore.PopulationValue].values[1]

            share_gdp_agriculture_2021 = DatabaseWitnessCore.ShareGlobalGDPAgriculture2021.value / 100.
            share_gdp_industry_2021 = DatabaseWitnessCore.ShareGlobalGDPIndustry2021.value / 100.
            share_gdp_services_2021 = DatabaseWitnessCore.ShareGlobalGDPServices2021.value / 100.

            # has to be in $/person : T$ x constant  / (Mperson) = M$/person = 1 000 000 $/person
            demand_agriculture_per_person_population_2021 = gdp_forecast[
                                                                1] * share_gdp_agriculture_2021 / population_2021 * 1e6
            demand_industry_per_person_population_2021 = gdp_forecast[
                                                             1] * share_gdp_industry_2021 / population_2021 * 1e6
            demand_services_per_person_population_2021 = gdp_forecast[
                                                             1] * share_gdp_services_2021 / population_2021 * 1e6
            demand_per_capita_agriculture = pd.DataFrame({GlossaryCore.Years: years,
                                                          GlossaryCore.SectorDemandPerCapitaDfValue: demand_agriculture_per_person_population_2021})

            demand_per_capita_industry = pd.DataFrame({GlossaryCore.Years: years,
                                                       GlossaryCore.SectorDemandPerCapitaDfValue: demand_industry_per_person_population_2021})

            demand_per_capita_services = pd.DataFrame({GlossaryCore.Years: years,
                                                       GlossaryCore.SectorDemandPerCapitaDfValue: demand_services_per_person_population_2021})

            invest_indus = pd.DataFrame(
                {GlossaryCore.Years: years,
                 GlossaryCore.ShareInvestment: invest_indus_start})

            invest_services = pd.DataFrame(
                {GlossaryCore.Years: years,
                 GlossaryCore.ShareInvestment: invest_services_start})

            invest_agriculture = pd.DataFrame(
                {GlossaryCore.Years: years,
                 GlossaryCore.ShareInvestment: invest_agri_start})

            # Energy
            share_energy_resi_2020 = DatabaseWitnessCore.EnergyshareResidential2020.value
            share_energy_other_2020 = DatabaseWitnessCore.EnergyshareOther2020.value
            share_energy_agri_2020 = DatabaseWitnessCore.EnergyshareAgriculture2020.value
            share_energy_services_2020 = DatabaseWitnessCore.EnergyshareServices2020.value
            share_energy_agriculture = pd.DataFrame({GlossaryCore.Years: years,
                                                     GlossaryCore.ShareSectorEnergy: share_energy_agri_2020})
            share_energy_services = pd.DataFrame({GlossaryCore.Years: years,
                                                  GlossaryCore.ShareSectorEnergy: share_energy_services_2020})
            share_energy_resi = pd.DataFrame({GlossaryCore.Years: years,
                                              GlossaryCore.ShareSectorEnergy: share_energy_resi_2020})
            share_energy_other = pd.DataFrame({GlossaryCore.Years: years,
                                               GlossaryCore.ShareSectorEnergy: share_energy_other_2020})

            brut_net = 1 / 1.45
            energy_outlook = pd.DataFrame({
                'year': [2000, 2005, 2010, 2017, 2018, 2025, 2030, 2035, 2040, 2050, 2060, 2100],
                'energy': [118.112, 134.122, 149.483879, 162.7848774, 166.4685636, 180.7072889, 189.6932084,
                           197.8418842,
                           206.1201182, 220.000, 250.0, 300.0]})
            f2 = interp1d(energy_outlook['year'], energy_outlook['energy'])
            # Find values for 2020, 2050 and concat dfs
            energy_supply = f2(np.arange(self.year_start, self.year_end + 1))
            energy_supply_values = energy_supply * brut_net

            energy_production = pd.DataFrame(
                {GlossaryCore.Years: years, GlossaryCore.TotalProductionValue: energy_supply_values * 0.7})

            # data for consumption
            temperature = np.linspace(1, 3, len(years))
            temperature_df = pd.DataFrame({GlossaryCore.Years: years, GlossaryCore.TempAtmo: temperature,
                                           GlossaryCore.TempOcean: temperature / 100})
            energy_price = np.arange(110, 110 + len(years))
            energy_mean_price = pd.DataFrame(
                {GlossaryCore.Years: years, GlossaryCore.EnergyPriceValue: energy_price})

            # workforce share
            agrishare = 27.4
            indusshare = 21.7
            serviceshare = 50.9
            workforce_share = pd.DataFrame({GlossaryCore.Years: years, GlossaryCore.SectorAgriculture: agrishare,
                                            GlossaryCore.SectorIndustry: indusshare,
                                            GlossaryCore.SectorServices: serviceshare})

            cons_input.update({
                f"{self.study_name}.{self.labormarket_name}.{'workforce_share_per_sector'}": workforce_share,
                f"{self.study_name}.{GlossaryCore.TemperatureDfValue}": temperature_df,
                f"{self.study_name}.{GlossaryCore.EnergyMeanPriceValue}": energy_mean_price,
                f'{self.study_name}.{self.macro_name}.{GlossaryCore.SectorAgriculture}.{GlossaryCore.SectorDemandPerCapitaDfValue}': demand_per_capita_agriculture,
                f"{self.study_name}.{self.macro_name}.{GlossaryCore.SectorAgriculture}.{GlossaryCore.ShareSectorInvestmentDfValue}": invest_agriculture,
                f'{self.study_name}.{self.macro_name}.{GlossaryCore.SectorIndustry}.{GlossaryCore.SectorDemandPerCapitaDfValue}': demand_per_capita_industry,
                f'{self.study_name}.{self.macro_name}.{GlossaryCore.SectorServices}.{GlossaryCore.SectorDemandPerCapitaDfValue}': demand_per_capita_services,
                f"{self.study_name}.{self.macro_name}.{GlossaryCore.SectorServices}.{GlossaryCore.ShareSectorInvestmentDfValue}": invest_services,
                f"{self.study_name}.{self.macro_name}.{GlossaryCore.SectorIndustry}.{GlossaryCore.ShareSectorInvestmentDfValue}": invest_indus,
                f"{self.study_name}.{self.macro_name}.{GlossaryCore.SectorServices}.{GlossaryCore.ShareSectorEnergyDfValue}": share_energy_services,
                f"{self.study_name}.{self.macro_name}.{GlossaryCore.SectorAgriculture}.{GlossaryCore.ShareSectorEnergyDfValue}": share_energy_agriculture,
                f"{self.study_name}.{GlossaryCore.ShareResidentialEnergyDfValue}": share_energy_resi,
                f"{self.study_name}.{self.redistrib_energy_name}.{GlossaryCore.ShareOtherEnergyDfValue}": share_energy_other,
                f"{self.study_name}.{GlossaryCore.EnergyProductionValue}": energy_production,
            })


        setup_data_list.append(cons_input)

        numerical_values_dict = {
            f'{self.study_name}.epsilon0': 1.0,
            f'{self.study_name}.max_mda_iter': 70,
            f'{self.study_name}.tolerance': 1.0e-10,
            f'{self.study_name}.n_processes': 1,
            f'{self.study_name}.linearization_mode': 'adjoint',
            f'{self.study_name}.sub_mda_class': 'MDAGaussSeidel'}

        setup_data_list.append(numerical_values_dict)

        return setup_data_list


if '__main__' == __name__:
    uc_cls = Study()
    uc_cls.test()

