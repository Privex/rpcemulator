.. _Privex JsonRPC Emulators documentation:



Privex JsonRPC Emulators documentation
=================================================

.. image:: https://www.privex.io/static/assets/svg/brand_text_nofont.svg
   :target: https://www.privex.io/
   :width: 400px
   :height: 400px
   :alt: Privex Logo
   :align: center

Welcome to the documentation for `Privex's JsonRPC Emulators`_ - a package designed to emulate common JsonRPC
APIs, such as ``bitcoind`` 's JsonRPC, allowing for unit/integration testing RPC-reliant code, without needing
the appropriate daemon installed (which could require a lot of configuration, synchronisation etc.).

This documentation is automatically kept up to date by ReadTheDocs, as it is automatically re-built each time
a new commit is pushed to the `Github Project`_ 

.. _Privex's JsonRPC Emulators: https://github.com/Privex/rpcemulator
.. _Github Project: https://github.com/Privex/rpcemulator

.. contents::


Quickstart
----------

**Installing with** `Pipenv`_ **(recommended)**

.. code-block:: bash

    pipenv install rpcemulator


**Installing with standard** ``pip3``

.. code-block:: bash

    pip3 install rpcemulator



.. _Pipenv: https://pipenv.kennethreitz.org/en/latest/


.. include:: ./examples.rst


Python Module Overview
======================

Below is a listing of the sub-modules available in ``rpcemulator`` with a short description of what each module
contains.

.. include:: ./code/index.rst


All Documentation
=================

.. toctree::
   :maxdepth: 8
   :caption: Main:

   self
   install
   examples


.. toctree::
   :maxdepth: 3
   :caption: Code Documentation:

   code/index

.. toctree::
   :caption: Unit Testing

   code/tests


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
