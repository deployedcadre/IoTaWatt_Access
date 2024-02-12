Overview
========

`IoTaWatt_Access <https://github.com/deployedcadre/IoTaWatt_Access>`_ provides a
Python interface to the `query API <https://docs.iotawatt.com/en/master/query.html>`_
of the `IoTaWatt <https://iotawatt.com/>`_ home electrical monitoring device. The
device provides support for automatic uploading of data to online energy monitoring
services, but no convenient tools for directly downloading the data. This packages
allows data to be downloaded and stored as `NumPy <https://numpy.org/>`_ arrays for
analysis and plotting.


Requirements
------------

This package requires Python 3.3 or later. The requirements for use of the package
and associated utility scripts are listed in the ``requirements.txt`` file in the
repository root directory. Additional requirements for building the documents are
listed in the file ``docs/requirements.txt``. The ``pytest`` package is required
to run the tests.


Usage
-----

The ``iotawatt_access`` module API is documented in :doc:`api`. The utility scripts
included in the ``bin`` directory also serve as usage examples for the ``iotatwatt_access``
module, and also provide useful functionality.
