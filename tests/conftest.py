import os
import json
import dateutil.parser
import pytest
import flask
import unicodecsv
import sqlalchemy

import babbage.api
import babbage.model
import babbage.manager

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture()
def app():
    app = flask.Flask('test')
    app.register_blueprint(babbage.api.blueprint, url_prefix='/bbg')
    app.config['DEBUG'] = True
    app.config['TESTING'] = True
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
    return app


@pytest.fixture
def fixtures_cube_manager(sqla_engine):
    path = os.path.join(FIXTURE_PATH, 'models')
    return babbage.manager.JSONCubeManager(sqla_engine, path)

@pytest.fixture
def load_api_fixtures(app, fixtures_cube_manager):
    return babbage.api.configure_api(app, fixtures_cube_manager)


@pytest.fixture
def simple_model_data():
    return load_json_fixture('models/simple_model.json')


@pytest.fixture
def simple_model(simple_model_data):
    return babbage.model.Model(simple_model_data)


@pytest.fixture()
def cra_model():
    return load_json_fixture('models/cra.json')


@pytest.fixture()
def cra_table(sqla_engine):
    return load_csv(sqla_engine, 'cra.csv')


@pytest.fixture()
def cap_or_cur_table(sqla_engine):
    return load_csv(sqla_engine, 'cap_or_cur.csv')


@pytest.fixture()
def load_fixtures(cra_table, cap_or_cur_table):
    pass


@pytest.fixture()
def sqla_engine():
    DATABASE_URI = os.environ.get('BABBAGE_TEST_DB')
    assert DATABASE_URI, 'Set the envvar BABBAGE_TEST_DB to a PostgreSQL URI'
    engine = sqlalchemy.create_engine(DATABASE_URI)

    try:
        yield engine
    finally:
        meta = sqlalchemy.MetaData(bind=engine, reflect=True)
        meta.drop_all()


def load_json_fixture(name):
    path = os.path.join(FIXTURE_PATH, name)
    with open(path, 'r') as fh:
        return json.load(fh)


def load_csv(sqla_engine, file_name, table_name=None):
    table_name = table_name or os.path.basename(file_name).split('.')[0]
    path = os.path.join(FIXTURE_PATH, file_name)
    table = None
    with open(path, 'rb') as fh:
        for row in unicodecsv.DictReader(fh):
            if table is None:
                table = _create_table(sqla_engine, table_name, row.keys())
            stmt = table.insert(_convert_row(row))
            sqla_engine.execute(stmt)
    return table


def _create_table(engine, table_name, columns):
    meta = sqlalchemy.MetaData()
    meta.bind = engine

    if engine.has_table(table_name):
        table = sqlalchemy.schema.Table(table_name, meta, autoload=True)
        table.drop()

    table = sqlalchemy.schema.Table(table_name, meta)
    id_col = sqlalchemy.schema.Column('_id', sqlalchemy.types.Integer, primary_key=True)
    table.append_column(id_col)
    for (_, name, typ) in sorted(_column_specs(columns)):
        col = sqlalchemy.schema.Column(name, typ)
        table.append_column(col)

    table.create(engine)
    return table


def _column_specs(columns):
    TYPES = {
        'string': sqlalchemy.types.Unicode,
        'integer': sqlalchemy.types.Integer,
        'bool': sqlalchemy.types.Boolean,
        'float': sqlalchemy.types.Float,
        'decimal': sqlalchemy.types.Float,
        'date': sqlalchemy.types.Date
    }
    for column in columns:
        spec = column.rsplit(':', 1)
        typ = 'string' if len(spec) == 1 else spec[1]
        yield column, spec[0], TYPES[typ]


def _convert_row(row):
    data = {}
    for (key, name, typ) in _column_specs(row.keys()):
        value = row.get(key)
        if not len(value.strip()):
            value = None
        elif typ == sqlalchemy.types.Integer:
            value = int(value)
        elif typ == sqlalchemy.types.Float:
            value = float(value)
        elif typ == sqlalchemy.types.Boolean:
            value = value.strip().lower()
            value = value in ['1', 'true', 'yes']
        elif typ == sqlalchemy.types.Date:
            value = dateutil.parser.parse(value).date()
        data[name] = value
    return data
