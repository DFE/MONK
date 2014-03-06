Release 0.1.6 (2014-03-06)
==========================

 * again bugs got fixed
 * most important topic was stabilizing the connect->login->cmd process
 * error handling improved with more ifs and more userfriendly exceptions
 * it is now possible to completely move from Disconnected to Authenticated
   even when the target device is just booting.

Release 0.1.5 (2014-02-25)
==========================

 * fixed many bugs
 * most notably 0.1.4 was actually not able to be installed from PyPI without
   workaround

Release 0.1.4 (2014-01-24)
==========================

 * fixed some urgent bugs
 * renamed harness to fixture
 * updated docs

Release 0.1.3
=============

 * complete reimplementation finished
 * documentation not up to date yet
 * Features are:
   * create independent connections with the connection layer
   * example implementation with SerialConnection
   * create complete device abstraction with the dev layer
   * basic device class in layer
   * separate test cases and connection data for reusage with harness layer
   * example parser for extendend INI implemented in harness layer

Release 0.1.2
=============

 * added GPLv3+ (source) and CC-BY-SA 3.0 (docs) Licenses
 * updated coding standards

Release 0.1.1
=============

 * rewrote documentation
 * style guide
 * configured for pip, setuptools, virtualenv
 * restarted unit test suite with nosetests
 * added development and test requirements



Release 0.1
===========

The initial Release.
