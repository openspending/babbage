# Babbage Analytical Engine

[![Build Status](https://travis-ci.org/spendb/babbage.svg?branch=master)](https://travis-ci.org/pudo/babbage)
[![Coverage Status](https://coveralls.io/repos/spendb/babbage/badge.svg?branch=master&service=github)](https://coveralls.io/github/spendb/babbage?branch=master)


``babbage`` is a lightweight implementation of an OLAP-style database
query tool for PostgreSQL. Given a database schema and a logical model
of the data, it can be used to perform analytical queries against that
data - programmatically or via a web API.

It is heavily inspired by [Cubes](http://cubes.databrewery.org/) but
has less ambitious goals, i.e. no pre-computation of aggregates, or
multiple storage backends.

## Installation and test

``babbage`` will normally included as a PyPI dependency, or installed via
``pip``:

```bash
$ pip install babbage
```

People interested in contributing to the package should instead check out the
source repository and then use the provided ``Makefile`` to install the
library (this requires ``virtualenv`` to be installed):

```bash
$ git clone https://github.com/spendb/babbage.git
$ cd babbage
$ make install
$ make test
```
