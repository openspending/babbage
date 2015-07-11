
test: install
	env/bin/nosetests --with-coverage --cover-package=babbage --cover-erase

.PHONY: install
install: env/bin/python

env/bin/python:
	virtualenv env
	env/bin/pip install --upgrade pip
	env/bin/pip install -e .
	env/bin/pip install nose coverage Flask-Testing unicodecsv python-dateutil

.PHONY: clean
clean:
	rm -rf env
