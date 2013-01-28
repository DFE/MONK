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

 add a TODO file, make a change to the ‘simplegit.rb’ file, and then make a commit with both changeshis suite implements a number of automated integration tests for the HidaV
platform. 


Test Framework
==============

Main page: :ref:`integration-test-framework`

In order to run the tests this suite provides a basic framework to
completely remote-control a device. This framework is applied by all the
integration tests to actually perform the tests.

Configuration Test Environment
==============================

In order to run tests you need a serial connection to the device. The srial ports for the connection have to be configured in some environment variables. The existing environment variables you find in :ref:`environment-variables`

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
