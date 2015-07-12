import os
from nose.tools import raises

from babbage.manager import JSONCubeManager
from babbage.cube import Cube
from babbage.exc import BabbageException


from .util import TestCase, FIXTURE_PATH


class CubeManagerTestCase(TestCase):

    def setUp(self):
        super(CubeManagerTestCase, self).setUp()
        path = os.path.join(FIXTURE_PATH, 'models')
        self.fixture_mgr = JSONCubeManager(self.engine, path)

    def test_list_cubes(self):
        cubes = list(self.fixture_mgr.list_cubes())
        assert len(cubes) == 2, cubes

    def test_has_cube(self):
        assert self.fixture_mgr.has_cube('cra')
        assert not self.fixture_mgr.has_cube('cro')

    def test_get_model(self):
        model = self.fixture_mgr.get_cube_model('cra')
        assert 'dimensions' in model

    @raises(BabbageException)
    def test_get_model_doesnt_exist(self):
        self.fixture_mgr.get_cube_model('cro')

    def test_get_cube(self):
        cube = self.fixture_mgr.get_cube('cra')
        assert isinstance(cube, Cube)

    @raises(BabbageException)
    def test_get_cube_doesnt_exist(self):
        self.fixture_mgr.get_cube('cro')
