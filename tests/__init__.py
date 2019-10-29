"""
This module contains test cases for Privex's JsonRPC Emulators (rpcemulator).

Testing pre-requisites
----------------------

    - Ensure you have any mandatory requirements installed (see setup.py's install_requires)
    - You may wish to install any optional requirements listed in README.md for best results
    - Python 3.7 is recommended at the time of writing this. See README.md in-case this has changed.

Running via PyTest
------------------

To run the tests, we strongly recommend using the ``pytest`` tool (used by default for our Travis CI)::

    # Install requirements.txt which should include PyTest
    user@host: ~/rpcemulator $ pip3 install -r requirements.txt
    # You can add `-v` for more detailed output, just like when running the tests directly.
    user@host: ~/rpcemulator $ pytest

    ===================================== test session starts =====================================
    platform darwin -- Python 3.7.0, pytest-5.0.1, py-1.8.0, pluggy-0.12.0
    rootdir: /home/user/rpcemulator
    collected 4 items

    tests/test_bitcoin.py ....                                                               [100%]


    ============================ 4 passed, 1 warnings in 0.17 seconds =============================

Running directly using Python Unittest
--------------------------------------

Alternatively, you can run the tests by hand with ``python3.7`` ( or just ``python3`` ) ::

    user@the-matrix ~/rpcemulator $ python3.7 -m tests
    ....
    ----------------------------------------------------------------------
    Ran 4 tests in 0.001s

    OK

For more verbosity, simply add ``-v`` to the end of the command::

    user@the-matrix ~/rpcemulator $ python3 -m tests -v
    test_getblockchaininfo (tests.test_bitcoin.TestBitcoinEmulator)
    Test that the ``getblockchaininfo`` JsonRPC call returns data as expected ... ok
    test_getnetworkinfo (tests.test_bitcoin.TestBitcoinEmulator)
    Test that the ``getnetworkinfo`` JsonRPC call returns data as expected ... ok
    test_getnewaddress (tests.test_bitcoin.TestBitcoinEmulator)
    Get a new address from the emulator and confirm it seems like a BTC address ... ok
    test_send_valid (tests.test_bitcoin.TestBitcoinEmulator)
    Test sending coins to external address creates a TX in listtransactions, and reduces the balance ... ok
    
    ----------------------------------------------------------------------
    Ran 4 tests in 0.242s
    
    OK




**Copyright**::

    Copyright 2019         Privex Inc.   ( https://www.privex.io )
    License: X11 / MIT     Github: https://github.com/Privex/rpcemulator


        +===================================================+
        |                 © 2019 Privex Inc.                |
        |               https://www.privex.io               |
        +===================================================+
        |                                                   |
        |        Originally Developed by Privex Inc.        |
        |                                                   |
        |        Core Developer(s):                         |
        |                                                   |
        |          (+)  Chris (@someguy123) [Privex]        |
        |          (+)  Kale (@kryogenic) [Privex]          |
        |                                                   |
        +===================================================+

    Copyright 2019     Privex Inc.   ( https://www.privex.io )

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
    Software, and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""

import logging
import unittest
from privex.loghelper import LogHelper
from privex.helpers import env_bool
from privex.rpcemulator.base import Emulator
from tests.test_bitcoin import TestBitcoinEmulator

Emulator.use_coverage = True

if env_bool('DEBUG', False) is True:
    LogHelper('privex.rpcemulator', level=logging.DEBUG).add_console_handler(logging.DEBUG)
else:
    LogHelper('privex.rpcemulator', level=logging.CRITICAL)  # Silence non-critical log messages
    Emulator.quiet = True    # Disable HTTP logging

if __name__ == '__main__':
    unittest.main()
