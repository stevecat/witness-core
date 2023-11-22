'''
Copyright 2023 Capgemini

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

from pandas import DataFrame, concat

from sostrades_core.study_manager.study_manager import StudyManager
from climateeconomics.sos_processes.iam.witness_sect_wo_energy.datacase_witness_wo_energy import \
    DataStudy as datacase_witness
from energy_models.sos_processes.energy.MDA.energy_process_v0_mda.usecase import Study as datacase_energy
from sostrades_core.execution_engine.func_manager.func_manager import FunctionManager
from sostrades_core.execution_engine.func_manager.func_manager_disc import FunctionManagerDisc
from sostrades_core.tools.post_processing.post_processing_factory import PostProcessingFactory
from climateeconomics.core.tools.ClimateEconomicsStudyManager import ClimateEconomicsStudyManager
from energy_models.core.energy_process_builder import INVEST_DISCIPLINE_OPTIONS

INEQ_CONSTRAINT = FunctionManagerDisc.INEQ_CONSTRAINT
AGGR_TYPE = FunctionManagerDisc.AGGR_TYPE
AGGR_TYPE_SUM = FunctionManager.AGGR_TYPE_SUM
AGGR_TYPE_SMAX = FunctionManager.AGGR_TYPE_SMAX
DEFAULT_COARSE_TECHNO_DICT = {'renewable': {'type': 'energy', 'value': ['RenewableSimpleTechno']},
                              'fossil': {'type': 'energy', 'value': ['FossilSimpleTechno']},
                              'carbon_capture': {'type': 'CCUS', 'value': ['direct_air_capture.DirectAirCaptureTechno',
                                                                           'flue_gas_capture.FlueGasTechno']},
                              'carbon_storage': {'type': 'CCUS', 'value': ['CarbonStorageTechno']}}
DEFAULT_ENERGY_LIST = [key for key, value in DEFAULT_COARSE_TECHNO_DICT.items(
) if value['type'] == 'energy']
DEFAULT_CCS_LIST = [key for key, value in DEFAULT_COARSE_TECHNO_DICT.items(
) if value['type'] == 'CCUS']


class Study(StudyManager):

    def __init__(self, year_start=2020, year_end=2100, time_step=1, bspline=True, run_usecase=True,
                 execution_engine=None,
                 invest_discipline=INVEST_DISCIPLINE_OPTIONS[2], techno_dict=DEFAULT_COARSE_TECHNO_DICT):
        super().__init__(__file__, run_usecase=run_usecase, execution_engine=execution_engine)
        self.year_start = year_start
        self.year_end = year_end
        self.time_step = time_step
        self.bspline = bspline
        self.invest_discipline = invest_discipline
        self.energy_list = DEFAULT_ENERGY_LIST
        self.ccs_list = DEFAULT_CCS_LIST
        self.dc_energy = datacase_energy(
            self.year_start, self.year_end, self.time_step, bspline=self.bspline, execution_engine=execution_engine,
            invest_discipline=self.invest_discipline, techno_dict=techno_dict)
        self.sub_study_path_dict = self.dc_energy.sub_study_path_dict

    def setup_process(self):
        datacase_energy.setup_process(self)


    def setup_usecase(self):
        setup_data_list = []

        # -- load data from energy pyworld3
        # -- Start with energy to have it at first position in the list...
        self.dc_energy.study_name = self.study_name
        self.energy_mda_usecase = self.dc_energy

        # -- load data from witness
        dc_witness = datacase_witness(
            self.year_start, self.year_end, self.time_step)
        dc_witness.study_name = self.study_name

        witness_input_list = dc_witness.setup_usecase()
        setup_data_list = setup_data_list + witness_input_list

        energy_input_list = self.dc_energy.setup_usecase()
        setup_data_list = setup_data_list + energy_input_list


        numerical_values_dict = {
            f'{self.study_name}.epsilon0': 1.0,
            f'{self.study_name}.max_mda_iter': 50,
            f'{self.study_name}.tolerance': 1.0e-10,
            f'{self.study_name}.n_processes': 1,
            f'{self.study_name}.linearization_mode': 'adjoint',
            f'{self.study_name}.sub_mda_class': 'GSPureNewtonMDA',
            f'{self.study_name}.cache_type': 'SimpleCache'}

        setup_data_list.append(numerical_values_dict)

        return setup_data_list


if '__main__' == __name__:
    uc_cls = Study(run_usecase=True)
    uc_cls.load_data()
    uc_cls.run()

    # ppf = PostProcessingFactory()
    # ll = ['Macroeconomics']
    # for disc in uc_cls.execution_engine.root_process.proxy_disciplines:
    #     for l in ll:
    #         if l in disc.sos_name:
    #             filters = ppf.get_post_processing_filters_by_discipline(
    #                 disc)
    #             graph_list = ppf.get_post_processing_by_discipline(
    #                 disc, filters, as_json=False)
    #
    #             for graph in graph_list:
    #                 graph.to_plotly().show()
