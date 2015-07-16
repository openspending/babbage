from sqlalchemy import func
from sqlalchemy.sql.expression import select

from babbage.query.cuts import Cuts  # noqa
from babbage.query.fields import Fields  # noqa
from babbage.query.drilldowns import Drilldowns  # noqa
from babbage.query.aggregates import Aggregates  # noqa
from babbage.query.ordering import Ordering  # noqa
from babbage.query.pagination import Pagination  # noqa


def count_results(cube, q):
    """ Get the count of records matching the query. """
    q = select(columns=[func.count(True)], from_obj=q.alias())
    return cube.engine.execute(q).scalar()


def generate_results(cube, q):
    """ Generate the resulting records for this query, applying pagination.
    Values will be returned by their reference. """
    if q._limit < 1:
        return
    rp = cube.engine.execute(q)
    while True:
        row = rp.fetchone()
        if row is None:
            return
        yield dict(row.items())


def first_result(cube, q):
    for row in generate_results(cube, q):
        return row
