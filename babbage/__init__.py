""" Babbage, an OLAP-like, light-weight database analytical engine. """

__version__ = "0.3.0"

from babbage.manager import CubeManager, JSONCubeManager  # noqa
from babbage.api import configure_api  # noqa
from babbage.validation import validate_model  # noqa
from babbage.exc import BabbageException, QueryException, BindingException  # noqa
