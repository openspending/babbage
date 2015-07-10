from setuptools import setup, find_packages

setup(
    name='babbage',
    version='0.0.1',
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
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
        'normality >= 0.2.2',
        "PyYAML >= 3.10",
        "six >= 1.7.3"
    ],
    tests_require=[],
    test_suite='test',
    entry_points={
        'console_scripts': [
        ]
    }
)
