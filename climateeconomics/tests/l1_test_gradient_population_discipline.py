'''
Copyright 2022 Airbus SAS

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

from climateeconomics.core.core_witness.climateeco_discipline import ClimateEcoDiscipline
from sostrades_core.execution_engine.execution_engine import ExecutionEngine
from sostrades_core.tests.core.abstract_jacobian_unit_test import AbstractJacobianUnittest
import pandas as pd
import numpy as np


class PopulationJacobianDiscTest(AbstractJacobianUnittest):
    
    def setUp(self):

        self.name = 'Test'
        self.ee = ExecutionEngine(self.name)
        self.model_name = 'population'
        ns_dict = {'ns_witness': f'{self.name}',
                   'ns_public': f'{self.name}'}

        self.ee.ns_manager.add_ns_def(ns_dict)

        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_witness.population.population_discipline.PopulationDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        self.ee.factory.set_builders_to_coupling_builder(builder)

        self.ee.configure()
        self.ee.display_treeview_nodes()

        data_dir = join(dirname(__file__), 'data')
        self.year_start = 2020
        self.year_end = 2100
        years = np.arange(self.year_start, self.year_end + 1)
        nb_per = self.year_end + 1 - self.year_start

        gdp_year_start = 130.187
        gdp_serie = []
        temp_serie = []
        gdp_serie.append(gdp_year_start)
        temp_serie.append(0.85)
        for year in np.arange(1, nb_per):
            gdp_serie.append(gdp_serie[year - 1] * 1.02)
            temp_serie.append(temp_serie[year - 1] * 1.01)

        self.economics_df_y = pd.DataFrame({'years': years, 'output_net_of_d': gdp_serie})
        self.economics_df_y.index = years
        self.temperature_df = pd.DataFrame({'years': years, 'temp_atmo': temp_serie})
        self.temperature_df.index = years

    def analytic_grad_entry(self):
        return [
            self.test_population_discipline_analytic_grad_output,
            self.test_population_discipline_analytic_grad_temperature,
            self.test_population_discipline_analytic_grad_big_gdp,
            self.test_population_discipline_analytic_big_pop,
            self.test_population_discipline_analytic_grad_big_temp,
            self.test_population_discipline_analytic_small_pop,
            self.test_population_discipline_analytic_grad_temp_negative
        ]

    def test_population_discipline_analytic_grad_output(self):
        '''
        Test gradient population wrt economics_df
        '''
        values_dict = {f'{self.name}.economics_df': self.economics_df_y,
                       f'{self.name}.year_start': self.year_start,
                       f'{self.name}.year_end': self.year_end,
                       f'{self.name}.temperature_df': self.temperature_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_population_discipline_output.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data, inputs=[f'{self.name}.economics_df'], outputs=[
                f'{self.name}.population_df'], step=1e-15, derr_approx='complex_step')

    def test_working_population_discipline_analytic_grad_output(self):
        '''
        Test gradient population wrt economics_df
        '''
        values_dict = {f'{self.name}.economics_df': self.economics_df_y,
                       f'{self.name}.year_start': self.year_start,
                       f'{self.name}.year_end': self.year_end,
                       f'{self.name}.temperature_df': self.temperature_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_working_population_discipline_output.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data, inputs=[f'{self.name}.economics_df'], outputs=[
                f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')
    
    def test_working_population_discipline_analytic_grad_temp(self):
        '''
        Test gradient population wrt economics_df
        '''
        values_dict = {f'{self.name}.economics_df': self.economics_df_y,
                       f'{self.name}.year_start': self.year_start,
                       f'{self.name}.year_end': self.year_end,
                       f'{self.name}.temperature_df': self.temperature_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_working_population_discipline_temp.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data, inputs=[f'{self.name}.temperature_df'], outputs=[
                f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_grad_temperature(self):
        '''
        Test gradient population wrt temperature_df
        '''

        values_dict = {f'{self.name}.economics_df': self.economics_df_y,
                       f'{self.name}.year_start': self.year_start,
                       f'{self.name}.year_end': self.year_end,
                       f'{self.name}.temperature_df': self.temperature_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_population_discipline_temp.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data,  inputs=[f'{self.name}.temperature_df'], outputs=[
                f'{self.name}.population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_grad_temp_negative(self):
        '''
        Test gradient population with negative temperature
        '''

        year_start = 2020
        year_end = 2050
        years = np.arange(year_start, year_end + 1)
        nb_per = year_end + 1 - year_start

        gdp_year_start = 130.5
        gdp_serie = []
        temp_serie = []
        gdp_serie.append(gdp_year_start)
        temp_serie.append(0.85)
        for year in np.arange(1, nb_per):
            gdp_serie.append(gdp_serie[year - 1] * 1.05)
            temp_serie.append(temp_serie[year - 1] - 0.85)
        economics_df_y = pd.DataFrame({'years': years, 'output_net_of_d': gdp_serie})
        economics_df_y.index = years
        temperature_df = pd.DataFrame({'years': years, 'temp_atmo': temp_serie})
        temperature_df.index = years

        values_dict = {f'{self.name}.economics_df': economics_df_y,
                       f'{self.name}.year_start': year_start,
                       f'{self.name}.year_end': year_end,
                       f'{self.name}.temperature_df': temperature_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_population_discipline_temp_neg.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data,  inputs=[f'{self.name}.economics_df', f'{self.name}.temperature_df'],
                            outputs=[
                                f'{self.name}.population_df',f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_grad_big_gdp(self):
        '''
        Test gradient population with big GDP
        '''

        year_start = 2020
        year_end = 2050
        years = np.arange(year_start, year_end + 1)
        nb_per = year_end + 1 - year_start

        gdp_year_start = 130.5
        gdp_serie = []
        temp_serie = []
        gdp_serie.append(gdp_year_start)
        temp_serie.append(0.85)
        for year in np.arange(1, nb_per):
            gdp_serie.append(gdp_serie[year - 1] * 1000)
            temp_serie.append(temp_serie[year - 1] * 1.02)
        economics_df_y = pd.DataFrame({'years': years, 'output_net_of_d': gdp_serie})
        economics_df_y.index = years
        temperature_df = pd.DataFrame({'years': years, 'temp_atmo': temp_serie})
        temperature_df.index = years

        values_dict = {f'{self.name}.economics_df': economics_df_y,
                       f'{self.name}.year_start': year_start,
                       f'{self.name}.year_end': year_end,
                       f'{self.name}.temperature_df': temperature_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_population_discipline_big_gdp.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data, inputs=[f'{self.name}.economics_df', f'{self.name}.temperature_df'],
                            outputs=[
                                f'{self.name}.population_df', f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_grad_big_temp(self):
        '''
        Test gradient population with big temp but not so big
        '''

        year_start = 2020
        year_end = 2050
        years = np.arange(year_start, year_end + 1)
        nb_per = year_end + 1 - year_start

        gdp_year_start = 130.5
        gdp_serie = []
        temp_serie = []
        gdp_serie.append(gdp_year_start)
        temp_serie.append(0.85)
        for year in np.arange(1, nb_per):
            gdp_serie.append(gdp_serie[year - 1] * 1.05)
            temp_serie.append(temp_serie[year - 1] + 8.05)
        economics_df_y = pd.DataFrame({'years': years, 'output_net_of_d': gdp_serie})
        economics_df_y.index = years
        temperature_df = pd.DataFrame({'years': years, 'temp_atmo': temp_serie})
        temperature_df.index = years

        values_dict = {f'{self.name}.economics_df': economics_df_y,
                       f'{self.name}.year_start': year_start,
                       f'{self.name}.year_end': year_end,
                       f'{self.name}.temperature_df': temperature_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_population_discipline_augmente_temp.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data, inputs=[f'{self.name}.economics_df', f'{self.name}.temperature_df'],
                            outputs=[
                                f'{self.name}.population_df',f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_small_pop(self):
        '''
        Test gradient population with small population
        '''

        year_start = 2020
        year_end = 2050
        years = np.arange(year_start, year_end + 1)
        nb_per = year_end + 1 - year_start

        gdp_year_start = 130.5
        gdp_serie = []
        temp_serie = []
        gdp_serie.append(gdp_year_start)
        temp_serie.append(0.85)
        for year in np.arange(1, nb_per):
            gdp_serie.append(gdp_serie[year - 1] * 1.02)
            temp_serie.append(temp_serie[year - 1] * 1.02)
        economics_df_y = pd.DataFrame({'years': years, 'output_net_of_d': gdp_serie})
        economics_df_y.index = years
        temperature_df = pd.DataFrame({'years': years, 'temp_atmo': temp_serie})
        temperature_df.index = years

        data_dir = join(dirname(__file__), 'data')
        pop_init_df = pd.read_csv(
            join(data_dir, 'population_by_age_2020_small.csv'))

        values_dict = {f'{self.name}.economics_df': economics_df_y,
                       f'{self.name}.year_start': year_start,
                       f'{self.name}.year_end': year_end,
                       f'{self.name}.temperature_df': temperature_df,
                       f'{self.name}.population_start': pop_init_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline

        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_population_discipline_small_pop.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data,  inputs=[f'{self.name}.economics_df', f'{self.name}.temperature_df'],
                            outputs=[
                                f'{self.name}.population_df',f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_big_pop(self):
        '''
        Test gradient population with big population
        '''


        data_dir = join(dirname(__file__), 'data')
        year_start = 2020
        year_end = 2050
        years = np.arange(year_start, year_end + 1)
        nb_per = year_end + 1 - year_start

        gdp_year_start = 130.5
        gdp_serie = []
        temp_serie = []
        gdp_serie.append(gdp_year_start)
        temp_serie.append(0.85)
        for year in np.arange(1, nb_per):
            gdp_serie.append(gdp_serie[year - 1] * 1.05)
            temp_serie.append(temp_serie[year - 1] * 1.02)
        economics_df_y = pd.DataFrame({'years': years, 'output_net_of_d': gdp_serie})
        economics_df_y.index = years
        temperature_df = pd.DataFrame({'years': years, 'temp_atmo': temp_serie})
        temperature_df.index = years

        pop_init_df = pd.read_csv(
            join(data_dir, 'population_by_age_2020_large.csv'))

        values_dict = {f'{self.name}.economics_df': economics_df_y,
                       f'{self.name}.year_start': year_start,
                       f'{self.name}.year_end': year_end,
                       f'{self.name}.temperature_df': temperature_df,
                       f'{self.name}.population_start': pop_init_df
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline

        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_population_discipline_big_pop.pkl',
                            discipline=disc_techno, local_data = disc_techno.local_data,  inputs=[f'{self.name}.economics_df', f'{self.name}.temperature_df'],
                            outputs=[
                                f'{self.name}.population_df',f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_w_climate_effect(self):
        '''
        Test gradient population with climate effect
        '''
        values_dict = {f'{self.name}.economics_df': self.economics_df_y,
                       f'{self.name}.year_start': self.year_start,
                       f'{self.name}.year_end': self.year_end,
                       f'{self.name}.temperature_df': self.temperature_df,
                       f'{self.name}.assumptions_dict':
                           {'compute_gdp': True,
                            'compute_damage_on_climate': True,
                            'activate_climate_effect_population': True
                            }
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        # AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_working_population_discipline_output.pkl',
                            discipline=disc_techno, local_data=disc_techno.local_data,
                            inputs=[f'{self.name}.economics_df'], outputs=[
                f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')

    def test_population_discipline_analytic_wo_climate_effect(self):
        '''
        Test gradient population without climate effect
        '''
        values_dict = {f'{self.name}.economics_df': self.economics_df_y,
                       f'{self.name}.year_start': self.year_start,
                       f'{self.name}.year_end': self.year_end,
                       f'{self.name}.temperature_df': self.temperature_df,
                       f'{self.name}.assumptions_dict':
                           {'compute_gdp': True,
                            'compute_damage_on_climate': True,
                            'activate_climate_effect_population': False
                            }
                       }

        self.ee.load_study_from_input_dict(values_dict)

        self.ee.execute()

        disc_techno = self.ee.root_process.proxy_disciplines[0].mdo_discipline_wrapp.mdo_discipline
        #AbstractJacobianUnittest.DUMP_JACOBIAN = True
        self.check_jacobian(location=dirname(__file__), filename=f'jacobian_working_population_discipline_analytic_wo_climate_effect_output.pkl',
                            discipline=disc_techno, local_data=disc_techno.local_data,
                            inputs=[f'{self.name}.economics_df'], outputs=[
                f'{self.name}.working_age_population_df'], step=1e-15, derr_approx='complex_step')