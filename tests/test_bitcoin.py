import unittest
from decimal import Decimal
from multiprocessing import Process
from time import sleep
from typing import List

from privex.jsonrpc import BitcoinRPC
from privex.rpcemulator import bitcoin


def _contains_tx(tx_list: List[dict], txid: str):
    for t in tx_list:
        if t['txid'] == txid:
            return True
    return False


class TestBitcoinEmulator(unittest.TestCase):
    emulator: bitcoin.BitcoinEmulator
    """Stores the :class:`.Process` returned from :py:func:`.bitcoin.j_server`"""
    
    EXTERNAL_ADDRESS = "13J8HRihYqEDYHAxLciryQYTjpxXcjYMmR"
    """A Bitcoin address considered 'foreign' for testing that sending reduces balance"""
    
    LOCAL_ADDRESS = "1PNgW6AgPZMys844kFS2dK4tt7F36MzLC8"
    """A Bitcoin address considered to be in the wallet"""
    
    rpc = BitcoinRPC()
    
    
    @classmethod
    def setUpClass(cls) -> None:
        """Launch the Bitcoin RPC emulator in the background on default port 8332"""
        bitcoin.BitcoinEmulator.use_coverage = True
        cls.emulator = bitcoin.BitcoinEmulator()
        sleep(2)
    
    @classmethod
    def tearDownClass(cls) -> None:
        """Shutdown the Bitcoin RPC emulator process"""
        cls.emulator.terminate()
    
    def test_getnetworkinfo(self):
        """Test that the ``getnetworkinfo`` JsonRPC call returns data as expected"""
        info = self.rpc.getnetworkinfo()
        self.assertIs(type(info), dict)
        self.assertIn('version', info)
        self.assertEqual(info['version'], 170100)
    
    def test_getblockchaininfo(self):
        """Test that the ``getblockchaininfo`` JsonRPC call returns data as expected"""
        info = self.rpc.getblockchaininfo()
        self.assertIs(type(info), dict)
        
        self.assertIs(type(info['headers']), int)
        self.assertIs(type(info['blocks']), int)
        self.assertIs(type(info['difficulty']), float)
        
        self.assertGreater(info['blocks'], 0)
        self.assertGreater(info['headers'], 0)

    def test_getnewaddress(self):
        """Get a new address from the emulator and confirm it seems like a BTC address"""
        addr = self.rpc.getnewaddress()
        self.assertIs(type(addr), str)
        self.assertGreater(len(addr), 20)
        self.assertEqual(addr[0], '1')
    
    def test_send_valid(self):
        """Test sending coins to external address creates a TX in listtransactions, and reduces the balance"""
        # First find out our starting balance, and make sure we have enough to do the send TX.
        starting_balance = self.rpc.getbalance()
        self.assertGreater(starting_balance, Decimal('0.002'))
        
        # Send 0.001 to the known "external address", which should reduce our balance.
        txid = self.rpc.sendtoaddress(self.EXTERNAL_ADDRESS, Decimal('0.001'))
        self.assertGreater(len(txid), 20)
        
        # Verify that the TXID returned by sendtoaddress actually exists in the transaction list
        tx_list = self.rpc.listtransactions()
        self.assertTrue(_contains_tx(tx_list, txid))

        # Check that our balance has dropped by 0.001 (with a 0.0001 tolerance, because floats are stupid)
        new_bal = self.rpc.getbalance()
        expected_bal = float(starting_balance - Decimal('0.001'))
        self.assertAlmostEqual(expected_bal, float(new_bal), delta=0.0001)
    
    def test_validate_address(self):
        """Test ``validateaddress`` with a valid and invalid address"""
        self.assertTrue(self.rpc.validateaddress('1Br7KPLQJFuS2naqidyzdciWUYhnMZAzKA')['isvalid'])
        self.assertFalse(self.rpc.validateaddress('NotAnAddress')['isvalid'])

    def test_get_transaction(self):
        """Test ``gettransaction`` returns the correct transaction"""
        tx = self.rpc.gettransaction('fccacaffcb0a0a104274f1caa0b710e5a58b78f774629bfdcae99d544750e655')
        self.assertEqual(tx['address'], '13LWnGV7fGCUA2a9QiByGFKXL27H1HDuYp')
        self.assertAlmostEqual(tx['amount'], 0.03, delta=0.000001)

        
        


