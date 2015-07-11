import os
import json

from flask import Flask
from flask.ext.testing import TestCase as FlaskTestCase

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures')


def load_json_fixture(name):
    path = os.path.join(FIXTURE_PATH, name)
    with open(path, 'rb') as fh:
        return json.load(fh)


class TestCase(FlaskTestCase):

    def create_app(self):
        app = Flask('test')
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
        return app

    def setUp(self):
        pass
        # init_db(self.app)

    def tearDown(self):
        pass
        # clean_db(self.app)
