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

from sos_trades_core.sos_processes.base_process_builder import BaseProcessBuilder


class ProcessBuilder(BaseProcessBuilder):

    # ontology information
    _ontology_data = {
        'label': 'WITNESS Forest V2 process',
        'description': '',
        'category': '',
        'version': '',
    }

    def get_builders(self):

        ns_scatter = self.ee.study_name

        ns_dict = {'ns_witness': ns_scatter,
                   'ns_forest': ns_scatter,
                   'ns_public': ns_scatter,
                   'ns_functions': ns_scatter,
                   'ns_agriculture': ns_scatter,
                   'ns_ccs': ns_scatter,
                   'ns_energy': ns_scatter,
                   'ns_ref': ns_scatter,
                   }

        mods_dict = {'Capital': 'climateeconomics.sos_wrapping.sos_wrapping_witness.non_use_capital_objective.non_use_capital_obj_discipline.NonUseCapitalObjectiveDiscipline'
                     }
        builder_list = self.create_builder_list(mods_dict, ns_dict=ns_dict)

        return builder_list
