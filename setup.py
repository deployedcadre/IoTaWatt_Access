#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ast import parse

from setuptools import setup

name = "iotawatt_access"
# See http://stackoverflow.com/questions/2058802
with open("iotawatt_access.py") as f:
    version = (
        parse(next(filter(lambda line: line.startswith("__version__"), f)))
        .body[0]
        .value.s
    )

py_modules = ["iotawatt_access"]

longdesc = """
IoTaWatt_Access provides a Python interface to the query API of the IoTaWatt home electrical monitoring device. The device provides support for automatic uploading of data to online energy monitoring services, but no convenient tools for directly downloading the data. This packages allows data to be downloaded and stored as NumPy arrays for analysis and plotting.
"""


setup(
    name=name,
    version=version,
    py_modules=py_modules,
    description="IoTaWatt_Access: a Python interface to the query API of the IoTaWatt home electrical monitoring device.",
    long_description=longdesc,
    keywords=["IoTaWatt", "electric power usage monitor"],
    platforms="Any",
    license="GPLv2+",
    url="https://github.com/deployedcadre/IoTaWatt_Access",
    author="Brendt Wohlberg",
    scripts=["bin/iotawatt_download", "bin/iotawatt_plot", "bin/iotawatt_status"],
    python_requires=">= 3.3",
    setup_requires=[],
    install_requires=["python-dateutil", "requests", "numpy", "matplotlib"],
    extras_require={
        "tests": ["pytest"],
        "docs": [
            "sphinx",
            "sphinxcontrib-napoleon",
            "sphinx-autodoc-typehints",
            "furo",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    zip_safe=True,
)
