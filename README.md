# Privex's JsonRPC Emulators

[![Documentation Status](https://readthedocs.org/projects/rpcemulator/badge/?version=latest)](https://rpcemulator.readthedocs.io/en/latest/?badge=latest) 
[![Build Status](https://travis-ci.com/Privex/rpcemulator.svg?branch=master)](https://travis-ci.com/Privex/rpcemulator) 
[![Codecov](https://img.shields.io/codecov/c/github/Privex/rpcemulator)](https://codecov.io/gh/Privex/rpcemulator)
[![PyPi Version](https://img.shields.io/pypi/v/rpcemulator.svg)](https://pypi.org/project/rpcemulator/)
![License Button](https://img.shields.io/pypi/l/rpcemulator) 
![PyPI - Downloads](https://img.shields.io/pypi/dm/rpcemulator)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rpcemulator) 
![GitHub last commit](https://img.shields.io/github/last-commit/Privex/rpcemulator)

Privex's RPC Emulators are various python modules using [jsonrpcserver](https://github.com/bcb/jsonrpcserver) to
emulate a certain type of JsonRPC node for use in unit testing. 


```
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
```

# Tl;Dr; Install and use Privex RPC Emulators

Install from PyPi (detailed install info at [Install](#Install))

```sh
pipenv install rpcemulator    # If you use pipenv (and you should!)
pip3 install rpcemulator      # Otherwise, standard pip installation
```

Quick example usage:

```python
from privex.rpcemulator.bitcoin import BitcoinEmulator
from privex.jsonrpc import BitcoinRPC

rpc = BitcoinRPC()
"""
You can interact with the emulated Bitcoin daemon with any JsonRPC library you prefer.
However, privex-jsonrpc comes as a dependency of rpcemulator for convenience :)
"""

with BitcoinEmulator():
    print('Balance is:', rpc.getbalance())
    print('Network info is:', rpc.getnetworkinfo())

```

# Table of Contents (Github README)

**NOTE:** The below Table of Contents is designed to work on Github. The links do NOT work on PyPi's description,
and may not work if you're reading this README.md elsewhere.


1. [General Information](#general-info)
    
2. [Install](#Install)

    2.1 [Via PyPi (pip)](#download-and-install-from-pypi)
    
    2.2 [Manually via Git](#alternative-manual-install-from-git)

3. [Documentation](#documentation)

4. [License](#License)

5. [Example Uses](#example-uses)

6. [Unit Tests](#unit-tests)

7. [Contributing](#contributing)


# General Info

Privex's RPC Emulators are various python modules using [jsonrpcserver](https://github.com/bcb/jsonrpcserver) to
emulate a certain type of JsonRPC node for use in unit testing. 

Currently there's only one emulator included: `bitcoin.BitcoinEmulator` which emulates a `bitcoind` RPC server,
allowing code which interacts with a `bitcoind` (or other bitcoind-based) node to be tested, without needing
to run the coin daemon.

This means you can test `bitcoind` interfacing code with continuous integration systems like 
[Travis CI](https://travis-ci.com), where you would normally be unable to run a full coin daemon.


# Install

### Download and install from PyPi 

**Using [Pipenv](https://pipenv.kennethreitz.org/en/latest/) (recommended)**

```sh
pipenv install rpcemulator
```

**Using standard Python pip** 

```sh
pip3 install rpcemulator
```

### (Alternative) Manual install from Git

**Option 1 - Use pip to install straight from Github**

```sh
pip3 install git+https://github.com/Privex/rpcemulator
```

**Option 2 - Clone and install manually**

```bash
# Clone the repository from Github
git clone https://github.com/Privex/rpcemulator
cd rpcemulator

# RECOMMENDED MANUAL INSTALL METHOD
# Use pip to install the source code
pip3 install .

# ALTERNATIVE MANUAL INSTALL METHOD
# If you don't have pip, or have issues with installing using it, then you can use setuptools instead.
python3 setup.py install
```

# Documentation

[![Read the Documentation](https://read-the-docs-guidelines.readthedocs-hosted.com/_images/logo-wordmark-dark.png)](
https://rpcemulator.readthedocs.io/en/latest/)

Full documentation for this project is available above (click the Read The Docs image), including:

 - How to install the application and it's dependencies 
 - How to use the various functions and classes
 - General documentation of the modules and classes for contributors

**To build the documentation:**

```bash
git clone https://github.com/Privex/rpcemulator
cd rpcemulator/docs
pip3 install -r requirements.txt

# It's recommended to run make clean to ensure old HTML files are removed
# `make html` generates the .html and static files in docs/build for production
make clean && make html

# After the files are built, you can live develop the docs using `make live`
# then browse to http://127.0.0.1:8100/
# If you have issues with content not showing up correctly, try make clean && make html
# then run make live again.
make live
```

# License

This Python module was created by [Privex Inc. of Belize City](https://www.privex.io), and licensed under the 
X11/MIT License.
See the file [LICENSE](https://github.com/Privex/rpcemulator/blob/master/LICENSE) for the license text.

**TL;DR; license:**

We offer no warranty. You can copy it, modify it, use it in projects with a different license, and even in commercial 
(paid for) software.

The most important rule is - you **MUST** keep the original license text visible (see `LICENSE`) in any copies.

# Example uses

**Using a JsonRPC emulator in a unit test**

```python
import unittest
from privex.rpcemulator.bitcoin import BitcoinEmulator
from privex.jsonrpc import BitcoinRPC

class TestMyThing(unittest.TestCase):
    emulator: BitcoinEmulator
    """Stores the :class:`.BitcoinEmulator` instance"""
    rpc = BitcoinRPC()
    """For this example, we're using our BitcoinRPC class and communicating with the RPC directly"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Launch the Bitcoin RPC emulator in the background on default port 8332"""
        cls.emulator = BitcoinEmulator()
    
    @classmethod
    def tearDownClass(cls) -> None:
        """Shutdown the Bitcoin RPC emulator process"""
        cls.emulator.terminate()

    def test_something(self):
        """Run whatever code depends on a Bitcoin RPC"""
        self.assertGreater(self.rpc.getbalance(), 0)

```

**Using a JsonRPC emulator in your code, with a Context Manager**

Use the appropriate emulator class with a `with` statement so the server is automatically stopped once you're
done querying it.

This prevents any risk of the web server process being leftover.

```python
from privex.rpcemulator.bitcoin import BitcoinEmulator
from privex.jsonrpc import BitcoinRPC

rpc = BitcoinRPC()
print('Starting BitcoinEmulator')

with BitcoinEmulator():
    print('Balance is:', rpc.getbalance())
    print('Network info is:', rpc.getnetworkinfo())

print('Stopped BitcoinEmulator')

```


# Unit Tests

Unit tests are stored in the `tests/` folder, which are split into several `test_xxxx` files.

We use [Travis CI](https://travis-ci.com/Privex/rpcemulator) for continuous integration, which runs the test
suite every time a new commit, tag, or branch is pushed to this Github repo.

We also use [CodeCov](https://codecov.io/gh/Privex/rpcemulator) which integrates with our Travis CI setup, and
provides test coverage statistics, so ourselves and contributors can visually see how much of the code is covered
by our unit tests 

TL;Dr; Run the tests:

```
pip3 install -r requirements.txt
pytest -v
```

For more information about using the unit tests, see the 
[How to use the unit tests](https://rpcemulator.readthedocs.io/en/latest/code/tests.html) section of 
the documentation. 

# Contributing

We're happy to accept pull requests, no matter how small.

Please make sure any changes you make meet these basic requirements:

 - Any code taken from other projects should be compatible with the MIT License
 - This is a new project, and as such, supporting Python versions prior to 3.4 is very low priority.
 - However, we're happy to accept PRs to improve compatibility with older versions of Python, as long as it doesn't:
   - drastically increase the complexity of the code
   - OR cause problems for those on newer versions of Python.

**Legal Disclaimer for Contributions**

Nobody wants to read a long document filled with legal text, so we've summed up the important parts here.

If you contribute content that you've created/own to projects that are created/owned by Privex, such as code or 
documentation, then you might automatically grant us unrestricted usage of your content, regardless of the open source 
license that applies to our project.

If you don't want to grant us unlimited usage of your content, you should make sure to place your content
in a separate file, making sure that the license of your content is clearly displayed at the start of the file 
(e.g. code comments), or inside of it's containing folder (e.g. a file named LICENSE). 

You should let us know in your pull request or issue that you've included files which are licensed
separately, so that we can make sure there's no license conflicts that might stop us being able
to accept your contribution.

If you'd rather read the whole legal text, it should be included as `privex_contribution_agreement.txt`.


# Thanks for reading!

**If this project has helped you, consider [grabbing a VPS or Dedicated Server from Privex](https://www.privex.io).**

**Prices start at as little as US$8/mo (we take cryptocurrency!)**
