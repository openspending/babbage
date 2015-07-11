from .util import TestCase, load_json_fixture, load_csv


class CubeTestCase(TestCase):

    def setUp(self):
        super(CubeTestCase, self).setUp()
        self.cra_model = load_json_fixture('cra.json')
        self.cra_table = load_csv('cra.csv')

    def test_table_exists(self):
        assert self.engine.has_table(self.cra_table.name)
