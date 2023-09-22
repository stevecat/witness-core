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
from climateeconomics.glossarycore import GlossaryCore
from sostrades_core.tools.post_processing.post_processing_factory import PostProcessingFactory
from sostrades_core.study_manager.study_manager import StudyManager

from pathlib import Path
from os.path import join, dirname
from numpy import asarray, arange, array
import pandas as pd
import numpy as np
from sostrades_core.execution_engine.func_manager.func_manager import FunctionManager
from sostrades_core.execution_engine.func_manager.func_manager_disc import FunctionManagerDisc

INEQ_CONSTRAINT = FunctionManagerDisc.INEQ_CONSTRAINT
OBJECTIVE = FunctionManagerDisc.OBJECTIVE
AGGR_TYPE = FunctionManagerDisc.AGGR_TYPE
AGGR_TYPE_SMAX = FunctionManager.AGGR_TYPE_SMAX
AGGR_TYPE_SUM = FunctionManager.AGGR_TYPE_SUM


class Study(StudyManager):

    def __init__(self, year_start=2020, year_end=2100, time_step=1, name='.Land_Use_V1', execution_engine=None,
                 extra_name=''):
        super().__init__(__file__, execution_engine=execution_engine)
        self.study_name = 'usecase'
        self.landuse_name = name
        self.year_start = year_start
        self.year_end = year_end
        self.time_step = time_step
        self.extra_name = extra_name

    def setup_usecase(self):
        years = np.arange(self.year_start, self.year_end + 1, 1)
        year_range = self.year_end - self.year_start + 1
        setup_data_list = []
        # private values economics operator pyworld3
        landuse_input = {}
        landuse_input[f"{self.study_name}.{GlossaryCore.YearStart}"] = self.year_start
        landuse_input[f"{self.study_name}.{GlossaryCore.YearEnd}"] = self.year_end

        data_dir = join(
            dirname(dirname(dirname(dirname(dirname(__file__))))), 'tests', 'data')
        land_demand_df = pd.read_csv(
            join(data_dir, 'land_demand.csv'))
        # cut land_demand_df to respect years of study case
        land_demand_df = land_demand_df.loc[land_demand_df[GlossaryCore.Years]
                                            >= self.year_start]
        land_demand_df = land_demand_df.loc[land_demand_df[GlossaryCore.Years]
                                            <= self.year_end]
        self.total_food_land_surface = pd.DataFrame(
            index=years,
            columns=[GlossaryCore.Years,
                     'total surface (Gha)'])
        self.total_food_land_surface[GlossaryCore.Years] = years
        self.total_food_land_surface['total surface (Gha)'] = np.linspace(
            5, 4, year_range)

        self.deforested_surface_df = pd.DataFrame(
            index=years,
            columns=[GlossaryCore.Years,
                     'forest_surface_evol'])
        self.deforested_surface_df[GlossaryCore.Years] = years
        self.deforested_surface_df['forest_surface_evol'] = np.linspace(
            -0.001, 0, year_range)

        landuse_input[self.study_name +
                      self.extra_name + '.land_demand_df'] = land_demand_df
        landuse_input[self.study_name +
                      '.total_food_land_surface'] = self.total_food_land_surface
        landuse_input[self.study_name +
                      '.forest_surface_df'] = self.deforested_surface_df

        setup_data_list.append(landuse_input)

        return setup_data_list


if '__main__' == __name__:
    uc_cls = Study()
    uc_cls.load_data()
    # uc_cls.execution_engine.set_debug_mode()
    uc_cls.run()

    ppf = PostProcessingFactory()
    for disc in uc_cls.execution_engine.root_process.proxy_disciplines:
        filters = ppf.get_post_processing_filters_by_discipline(
            disc)
        graph_list = ppf.get_post_processing_by_discipline(
            disc, filters, as_json=False)

        for graph in graph_list:
            graph.to_plotly().show()
