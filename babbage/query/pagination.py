from babbage.query.parser import Parser
from babbage.util import parse_int


class Pagination(Parser):
    """ Handle pagination of results. Not actually using a parser. """

    def apply(self, q, page, page_size, page_max=10000):
        page_size = parse_int(page_size)
        if page_size is None:
            page_size = page_max
        limit = max(0, min(page_max, page_size))
        q = q.limit(limit)
        offset = (max(1, parse_int(page)) - 1) * limit
        if offset > 0:
            q = q.offset(offset)
        return q
