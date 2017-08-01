import pytest

from babbage.cube import Cube
from babbage.exc import BabbageException


@pytest.mark.usefixtures('load_api_fixtures')
class TestCubeManager(object):
    def test_list_cubes(self, fixtures_cube_manager):
        cubes = list(fixtures_cube_manager.list_cubes())
        assert len(cubes) == 2, cubes

    def test_has_cube(self, fixtures_cube_manager):
        assert fixtures_cube_manager.has_cube('cra')
        assert not fixtures_cube_manager.has_cube('cro')

    def test_get_model(self, fixtures_cube_manager):
        model = fixtures_cube_manager.get_cube_model('cra')
        assert 'dimensions' in model

    def test_get_model_doesnt_exist(self, fixtures_cube_manager):
        with pytest.raises(BabbageException):
            fixtures_cube_manager.get_cube_model('cro')

    def test_get_cube(self, fixtures_cube_manager):
        cube = fixtures_cube_manager.get_cube('cra')
        assert isinstance(cube, Cube)

    def test_get_cube_doesnt_exist(self, fixtures_cube_manager):
        with pytest.raises(BabbageException):
            fixtures_cube_manager.get_cube('cro')
