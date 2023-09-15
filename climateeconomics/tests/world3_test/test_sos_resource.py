from climateeconomics.core.core_world3.resource import Resource

import unittest

from sostrades_core.execution_engine.execution_engine import ExecutionEngine


def intialize_pyworld3_resource_inputs():
    obj = Resource()
    data = {GlossaryCore.YearStart: 1900,
            GlossaryCore.YearEnd: 2100,
            GlossaryCore.TimeStep: 0.5,
            'pyear': 1975}
    obj.set_data(data)
    obj.init_resource_constants()
    obj.init_resource_variables()
    obj.init_exogenous_inputs()
    obj.set_resource_table_functions()
    obj.set_resource_table_functions()
    obj.set_resource_delay_functions()
    obj.run_resource()
    return (obj)

def create_resource_input(name):
    ref = intialize_pyworld3_resource_inputs()

    values_dict = {name + ".pop": ref.pop,
                   name + ".iopc": ref.iopc}

    return values_dict


class TestSoSResource(unittest.TestCase):
    """
    SoSDiscipline test class
    """
    def setUp(self):
        '''
        Initialize third data needed for testing
        '''
        self.name = 'Test'
        self.model_name = 'Agriculture'
        self.ee = ExecutionEngine(self.name)

    def test_01_instantiate_sosdiscipline(self):
        '''
        default initialisation test
        '''

        ns_dict = {'ns_data': f'{self.name}.{self.model_name}',
                   'ns_coupling': f'{self.name}.{self.model_name}'}
        self.ee.ns_manager.add_ns_def(ns_dict)

        # Get discipline builder using path
        mod_path = 'climateeconomics.sos_wrapping.sos_wrapping_world3.resource_discipline.ResourceDiscipline'
        builder = self.ee.factory.get_builder_from_module(
            self.model_name, mod_path)

        # Set builder in factory and configure
        self.ee.factory.set_builders_to_coupling_builder(builder)
        self.ee.configure()

        # Set input values

        values_dict = create_resource_input(f'{self.name}.{self.model_name}')

        values_dict[f'{self.name}.{self.model_name}' + GlossaryCore.YearStart] = 1900
        values_dict[f'{self.name}.{self.model_name}' + GlossaryCore.YearEnd] = 2100
        values_dict[f'{self.name}.{self.model_name}' + GlossaryCore.TimeStep] = 0.5
        values_dict[f'{self.name}.{self.model_name}' + 'pyear'] = 1975

        # print(data_dir)


        # Configure process with input values
        self.ee.load_study_from_input_dict(values_dict)

        # Execute process
        self.ee.execute()