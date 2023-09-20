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
from climateeconomics.sos_wrapping.sos_wrapping_sectors.sector_discipline import SectorDiscipline


class AgricultureDiscipline(SectorDiscipline):
    "Agriculture sector discpline"
    sector_name = GlossaryCore.SectorAgriculture
    # ontology information
    _ontology_data = {
        'label': 'Agriculture sector WITNESS Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fa-solid fa-building-wheat',
        'version': '',
    }
    _maturity = 'Research'

    prod_cap_unit = 'T$'

    # update default values:
    DESC_IN = SectorDiscipline.DESC_IN
    DESC_IN['productivity_start']['default'] = 1.31162
    DESC_IN['capital_start']['default'] = 6.92448579
    DESC_IN['productivity_gr_start']['default'] = 0.0027844
    DESC_IN['decline_rate_tfp']['default'] = 0.098585
    DESC_IN['energy_eff_k']['default'] = 0.1
    DESC_IN['energy_eff_cst']['default'] = 0.490463
    DESC_IN['energy_eff_xzero']['default'] = 1993
    DESC_IN['energy_eff_max']['default'] = 2.35832
    DESC_IN['output_alpha']['default'] = 0.99

