.. Hidav Integration Test Tooling documentation master file, created by
   sphinx-quickstart on Thu Aug  9 11:10:24 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Hidav Integration Test Tooling's documentation!
**********************************************************

.. include:: undocumented.inc

Integration Test Implementations
================================

Main page: :ref:`integration-test-impl`

This suite implements a number of automated integration tests for the HidaV
platform. 


Test Framework
==============

Main page: :ref:`integration-test-framework`

In order to run the tests this suite provides a basic framework to
completely remote-control a device. This framework is applied by all the
integration tests to actually perform the tests.

Configuration Test Environment
==============================

In order to run tests you need two serial connection to the device. One connection to have access to a console and an other to communicate with the board controller. The serial ports for the connection have to be configured in some environment variables. You can find the existing environment variables in :ref:`environment-variables`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Complete Table of Contents
==========================
.. toctree::
   :maxdepth: 2

   test-framework.rst
