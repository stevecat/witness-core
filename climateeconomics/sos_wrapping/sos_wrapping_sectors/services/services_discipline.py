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
from climateeconomics.glossarycore import GlossaryCore
from climateeconomics.sos_wrapping.sos_wrapping_sectors.sector_discipline import SectorDiscipline


class ServicesDiscipline(SectorDiscipline):
    "Services sector discpline"
    sector_name = GlossaryCore.SectorServices

    # ontology information
    _ontology_data = {
        'label': 'Services sector WITNESS Model',
        'type': 'Research',
        'source': 'SoSTrades Project',
        'validated': '',
        'validated_by': 'SoSTrades Project',
        'last_modification_date': '',
        'category': '',
        'definition': '',
        'icon': 'fa-solid fa-building-user',
        'version': '',
    }
    _maturity = 'Research'

    DESC_IN = SectorDiscipline.DESC_IN
    DESC_IN['productivity_start']['default'] = 0.1328496
    DESC_IN['capital_start']['default'] = 281.2092
    DESC_IN['productivity_gr_start']['default'] = 0.00161432
    DESC_IN['decline_rate_tfp']['default'] = 0.088925
    DESC_IN['energy_eff_k']['default'] = 0.04383
    DESC_IN['energy_eff_cst']['default'] = 3.12565
    DESC_IN['energy_eff_xzero']['default'] = 2044.09
    DESC_IN['energy_eff_max']['default'] = 0.594575
    DESC_IN['output_alpha']['default'] = 0.99
    DESC_IN['depreciation_capital']['default'] = 0.058
    
