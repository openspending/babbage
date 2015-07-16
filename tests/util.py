import os
import json
import unicodecsv
import dateutil.parser
from sqlalchemy import MetaData, create_engine, types, schema

from flask import Flask
from flask.ext.testing import TestCase as FlaskTestCase

from babbage.api import blueprint

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures')
DATABASE_URI = os.environ.get('BABBAGE_TEST_DB')
assert DATABASE_URI, 'Set the envvar BABBAGE_TEST_DB to a PostgreSQL URI'
engine = create_engine(DATABASE_URI)

TYPES = {
    'string': types.Unicode,
    'integer': types.Integer,
    'bool': types.Boolean,
    'float': types.Float,
    'decimal': types.Float,
    'date': types.Date
}


def load_json_fixture(name):
    path = os.path.join(FIXTURE_PATH, name)
    with open(path, 'rb') as fh:
        return json.load(fh)


def column_specs(columns):
    for column in columns:
        spec = column.rsplit(':', 1)
        typ = 'string' if len(spec) == 1 else spec[1]
        yield column, spec[0], TYPES[typ]


def create_table(table_name, columns):
    meta = MetaData()
    meta.bind = engine

    if engine.has_table(table_name):
        table = schema.Table(table_name, meta, autoload=True)
        table.drop()

    table = schema.Table(table_name, meta)
    id_col = schema.Column('_id', types.Integer, primary_key=True)
    table.append_column(id_col)
    for (_, name, typ) in sorted(column_specs(columns)):
        col = schema.Column(name, typ)
        table.append_column(col)

    table.create(engine)
    return table


def convert_row(row):
    data = {}
    for (key, name, typ) in column_specs(row.keys()):
        value = row.get(key)
        if not len(value.strip()):
            value = None
        elif typ == types.Integer:
            value = int(value)
        elif typ == types.Float:
            value = float(value)
        elif typ == types.Boolean:
            value = value.strip().lower()
            value = value in ['1', 'true', 'yes']
        elif typ == types.Date:
            value = dateutil.parser.parse(value).date()
        data[name] = value
    return data


def load_csv(file_name, table_name=None):
    table_name = table_name or os.path.basename(file_name).split('.')[0]
    path = os.path.join(FIXTURE_PATH, file_name)
    table = None
    with open(path, 'rb') as fh:
        for row in unicodecsv.DictReader(fh):
            if table is None:
                table = create_table(table_name, row.keys())
            stmt = table.insert(convert_row(row))
            engine.execute(stmt)
    return table


def drop_tables():
    meta = MetaData(bind=engine, reflect=True)
    meta.drop_all()


class TestCase(FlaskTestCase):

    def create_app(self):
        app = Flask('test')
        app.register_blueprint(blueprint, url_prefix='/bbg')
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
        return app

    def setUp(self):
        # drop_tables()
        self.engine = engine

    def tearDown(self):
        pass
        # drop_tables()
