# Babbage Analytical Engine

``babbage`` is a lightweight implementation of an OLAP-style database
query tool for PostgreSQL. Given a database schema and a logical model
of the data, it can be used to perform analytical queries against that
data - programmatically or via a web API.

It is heavily inspired by [Cubes](http://cubes.databrewery.org/) but
has less ambitious goals, i.e. no pre-computation of aggregates, or
multiple storage backends.
