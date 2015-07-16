from setuptools import setup, find_packages

try:
    from babbage import __version__
except ImportError:
    __version__ = 'dev'

setup(
    name='babbage',
    version=__version__,
    description="A light-weight analytical engine for OLAP processing",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3'
    ],
    keywords='sql sqlalchemy olap cubes analytics',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://github.com/pudo/babbage',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    package_data={
        '': ['babbage/schema/model.json', 'babbage/schema/parser.ebnf']
    },
    zip_safe=False,
    install_requires=[
        'normality >= 0.2.2',
        'PyYAML >= 3.10',
        'six >= 1.7.3',
        'flask >= 0.10.1',
        'jsonschema >= 2.5.1',
        'sqlalchemy >= 1.0',
        'psycopg2 >= 2.6',
        'grako >= 3.6.1'
    ],
    tests_require=[
        'nose >= 1.3.7',
        'Flask-Testing >= 0.4.2',
        'python-dateutil-2.4.2',
        'unicodecsv-0.13.0'
    ],
    test_suite='tests',
    entry_points={}
)
