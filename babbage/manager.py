import os
import json
from abc import ABCMeta, abstractmethod

from babbage.cube import Cube
from babbage.exc import BabbageException


class CubeManager(object):
    """ A cube manager is responsible for locating and loading cube metadata,
    i.e. given a certain model name, it will locate that mode. This is an
    abstract base class for concrete implementations (e.g. file-based or
    application-specific). """
    __metaclass__ = ABCMeta

    def __init__(self, engine):
        self.engine = engine

    @abstractmethod
    def list_cubes(self):  # pragma: no cover
        """ List the available cubes, returning a name string for each available
        cube in the local system. """
        pass

    @abstractmethod
    def has_cube(self, name):  # pragma: no cover
        """ Given a cube name, check if a cube of that name exists. Returns
        a boolean. """
        pass

    def get_cube_model(self, name):  # pragma: no cover
        """ Given a cube name, return the model specification (as a dict) for
        that cube. This can also return a ``Model`` instance. """
        pass

    def get_engine(self):
        """ Method to get a SQLAlchemy engine object on which all further
        query operations will be conducted. """
        return self.engine

    def get_cube(self, name):
        """ Given a cube name, construct that cube and return it. Do not
        overwrite this method unless you need to. """
        return Cube(self.get_engine(), name, self.get_cube_model(name))


class JSONCubeManager(CubeManager):
    """ A sample implmentation of a cube manager based on a directory filled
    with JSON model descriptions. """

    def __init__(self, engine, directory):
        super(JSONCubeManager, self).__init__(engine)
        self.directory = directory

    def list_cubes(self):
        """ List all available JSON files. """
        for file_name in os.listdir(self.directory):
            if '.' in file_name:
                name, ext = file_name.rsplit('.', 1)
                if ext.lower() == 'json':
                    yield name

    def has_cube(self, name):
        """ Check if a cube exists. """
        return name in self.list_cubes()

    def get_cube_model(self, name):
        if not self.has_cube(name):
            raise BabbageException('No such cube: %r' % name)
        file_name = os.path.join(self.directory, name + '.json')
        with open(file_name, 'r') as fh:
            return json.load(fh)


class CachingJSONCubeManager(JSONCubeManager):
    """A simple extension of a JSONCubeManager keeping initialising each
    cube only once and returning initilised cubes on subsequent calls"""

    def __init__(self, engine, directory):
        super(CachingJSONCubeManager, self).__init__(engine, directory)
        self._cubes = {}
        self._cube_names = set(super(CachingJSONCubeManager, self).list_cubes())

    def list_cubes(self):
        return self._cube_names

    def has_cube(self, name):
        return name in self._cube_names

    def get_cube(self, name):
        if name not in self._cubes:
            self._cubes[name] = super(CachingJSONCubeManager, self).get_cube(name)
        return self._cubes[name]
