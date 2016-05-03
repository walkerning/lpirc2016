# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath((__file__)))

# meta infos
NAME = "nics_lpirc"
DESCRIPTION = "lpirc2016 codes"
VERSION = "0.1"

AUTHOR = "foxfi"
EMAIL = "foxdoraame@gmail.com"

# package contents
MODULES = []
PACKAGES = find_packages(exclude=["tests", "tests.*"])

# dependencies
INSTALL_REQUIRES = [
    "numpy>=1.8",
    "toml"
]
TESTS_REQUIRE = []

# entry points
ENTRY_POINTS = """
[console_scripts]
lpirc_detect=nics_lpirc.runner:main
lpirc_vis=nics_lpirc.visualize:visualize
lpirc_detect_prof=nics_lpirc.profiling_run:main
"""

def read_long_description(filename):
    path = os.path.join(here, filename)
    if os.path.exists(path):
        return open(path).read()
    return ''

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read_long_description('README.md'),
    author=AUTHOR,
    author_email=EMAIL,

    py_modules=MODULES,
    packages=PACKAGES,

    entry_points=ENTRY_POINTS,
    zip_safe=True,
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRE,
)
