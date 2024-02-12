IoTaWatt_Access
===============

.. image:: https://img.shields.io/badge/python-3.3+-green.svg
    :target: https://github.com/deployedcadre/IoTaWatt_Access
    :alt: Supported Python Versions

.. image:: https://readthedocs.org/projects/iotawatt-access/badge/?version=latest
    :target: https://iotawatt-access.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


IoTaWatt_Access provides a Python interface to the
`query API <https://docs.iotawatt.com/en/master/query.html>`_ of the
`IoTaWatt <https://iotawatt.com/>`_ home electrical monitoring device. The device
provides support for automatic uploading of data to online energy monitoring services,
but no convenient tools for directly downloading the data. This packages allows
data to be downloaded and stored as `NumPy <https://numpy.org/>`_ arrays for analysis
and plotting.


Requirements
------------

This package requires Python 3.3 or later. The requirements for use of the package
and associated utility scripts are listed in the ``requirements.txt`` file in the
repository root directory. Additional requirements for building the documents are
listed in the file ``docs/requirements.txt``. The ``pytest`` package is required
to run the tests.


Usage
-----

Aside from providing useful functionality, the utility scripts included in the
``bin`` directory also serve as usage examples for the ``iotatwatt_access`` module.


Documentation
-------------

Documentation may be built using the ``Makefile`` in the ``docs`` directory.


Contact
-------

Please submit bug reports, feature requests, etc. via the
`GitHub Issues interface <https://github.com/deployedcadre/IoTaWatt_Access/issues>`_.


License
-------

This package is made available under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2 of the License (see
the included ``LICENSE`` file), or (at your option) any later version.
