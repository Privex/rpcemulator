Example Usages
==============


Using a JsonRPC emulator in a unit test
---------------------------------------

.. code-block:: python

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



Using a JsonRPC emulator in your code, with a Context Manager
-------------------------------------------------------------

Use the appropriate emulator class with a ``with`` statement so the server is automatically stopped once you're
done querying it.

This prevents any risk of the web server process being leftover.

.. code-block:: python

    from privex.rpcemulator.bitcoin import BitcoinEmulator
    from privex.jsonrpc import BitcoinRPC

    rpc = BitcoinRPC()
    print('Starting BitcoinEmulator')

    with BitcoinEmulator():
        print('Balance is:', rpc.getbalance())
        print('Network info is:', rpc.getnetworkinfo())

    print('Stopped BitcoinEmulator')
