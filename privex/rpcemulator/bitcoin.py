"""
Bitcoin RPC emulator - emulates a limited bitcoind JsonRPC API

While the emulation isn't complete (at the time of writing), nor does it perfectly emulate bitcoind, it's still
very close, and implements methods such as :py:func:`.sendtoaddress` with balance checking, address "validation",
and automatically stores the send transaction (and receive TX if internal address).

To allow the RPC to be usable immediately, three ``receive`` transactions are included by default inside of
:py:attr:`.internal` - allowing you to send from these addresses with no additional configuration.


  * 1PNgW6AgPZMys844kFS2dK4tt7F36MzLC8 has 0.10 BTC
  * 1CGzMWXH6JhSKrkrbcGhRtEJxrU1za23LW has 0.05 BTC
  * 13LWnGV7fGCUA2a9QiByGFKXL27H1HDuYp has 0.03 BTC


Basic Usage::

    >>> from privex.rpcemulator.bitcoin import BitcoinEmulator
    >>> btc_rpc = BitcoinEmulator()
    >>> # make some queries to the RPC at https://127.0.0.1:8332
    >>> from privex.jsonrpc import BitcoinRPC
    >>> jr = BitcoinRPC()
    >>> print('Balance is:', jr.getbalance())
    >>> # once you're done, terminate the process
    >>> btc_rpc.terminate()



"""
import random
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Union, Dict, List, Tuple, Optional
from jsonrpcserver import method
from faker import Faker
from privex.helpers import is_true, dec_round

from privex.rpcemulator.base import Emulator

log = logging.getLogger(__name__)

internal = {
    "transactions": [
        dict(
            account='', address='1PNgW6AgPZMys844kFS2dK4tt7F36MzLC8', amount=Decimal('0.1'), category='receive',
            txid='db3f9b83bc7c53483e98a8714b61fc667772e1856333f290e2543186947ee939', confirmations=5, time=1572020407,
            label='', vout=0, generated=False
        ),
        dict(
            account='', address='13LWnGV7fGCUA2a9QiByGFKXL27H1HDuYp', amount=Decimal('0.03'), category='receive',
            txid='fccacaffcb0a0a104274f1caa0b710e5a58b78f774629bfdcae99d544750e655', confirmations=26, time=1572279928,
            label='', vout=0, generated=False
        ),
        dict(
            account='', address='1CGzMWXH6JhSKrkrbcGhRtEJxrU1za23LW', amount=Decimal('0.05'), category='receive',
            txid='e20ec2d1d56c7a2cc286a323ab4af4a990d9d23ca779ef1b0c0ad8e337e76d87', confirmations=28, time=1571928625,
            label='', vout=0, generated=False
        ),
    
    ],
    "addresses": [
        '13LWnGV7fGCUA2a9QiByGFKXL27H1HDuYp', '12Q3qTYGfgYwFC8Df2bgR7SqrQ5LcvkmhV',
        '1CGzMWXH6JhSKrkrbcGhRtEJxrU1za23LW',
        '18VstwHr1CWYPremjpJWTDNQvJmrPbdoef', '1GrZfggs26g3MMfATeRZCt2nEMmMSpJtVb',
        '1Br7KPLQJFuS2naqidyzdciWUYhnMZAzKA',
        '1ni4jkof1JAiuG7r3cnnDaCh9pk1gXZCG', '1Zr95UjPJBrUM8yXojNCYEjiX7uvbg6vM', '12AAGLe6BCoTfH1sKBXyUkzhSADoNgreAY',
        '1eS2hvVhiiA56hKd5JVMu9GrYvyLqfZ6q', '1PiXyqVnqv3TjEmBNESU3ZcTktZUZyZqnz', '1ASCd3gLBkMUtXXgLSMESUjAakth5iqvHM',
        '18iHXvsy57NiNmC7rWRm5X6rW6DSzWPAhP', '1BNqgLyNTFbFjGLR4sQMDX8E1F3rM8KBzT',
        '1ALEM4xrGPjSfcmLGica1Ygf3gsy9oPJgP',
        '1PNgW6AgPZMys844kFS2dK4tt7F36MzLC8', '1JBLYpceHDrPkhzWvP4o5bPo7tFMHPEYJ3',
        '1GWh8RfFDZrD9ooSAUpNQhUsFyyHaRfUye',
        '1J2VishkhGviaEZA5dYgrqW1bjV8JGKFj', '1MuncCP7uUicoL7bouyemZ3XqL5fC33J5V',
    ],
    "external_addresses": [
        "13J8HRihYqEDYHAxLciryQYTjpxXcjYMmR", "165GagcJtj4LtvM94BDrM2nfBfnfX1gQxc",
        "17EZkTedEnhEHe6yyy48YX1goAuP92DMUy", "1L5mrvowocD5rZdHWSBeacBZzMxAeGY6Rj",
    ],
    "getblockchaininfo":  dict(
        chain="main", blocks=601440, headers=601440,
        bestblockhash="00000000000000000000d6e50e9a20b98936b7833069a30e1e86c3d722d8a176", difficulty=13691480038694.45,
        mediantime=1572303763, verificationprogress=0.9999950714588575, initialblockdownload=False,
        chainwork="000000000000000000000000000000000000000009a65702bd04b8615352b4f7", size_on_disk=279953979777,
        pruned=False, softforks=[], bip9_softforks={}, warnings=""
    ),
    "getnetworkinfo":     dict(
        version=170100, subversion="/Satoshi:0.17.1/", protocolversion=70015, localservices="000000000000040d",
        localrelay=True, timeoffset=0, networkactive=True, connections=8,
        networks=[
            dict(name="ipv4", limited=False, reachable=True, proxy="", proxy_randomize_credentials=False),
            dict(name="ipv6", limited=False, reachable=True, proxy="", proxy_randomize_credentials=False),
            dict(name="onion", limited=True, reachable=False, proxy="", proxy_randomize_credentials=False)
        ],
        relayfee=0.00001000, incrementalfee=0.00001000,
        localaddresses=[
            dict(address="127.0.0.1", port=8333, score=1),
            dict(address="::1", port=8333, score=1)
        ],
        warnings=""
    )
}
"""
This module attribute is used as in-memory storage for various data, such as:
 
 * ``transactions`` - A list of incoming and outgoing wallet transactions. Some are pre-defined to ensure some
   addresses have a balance for immediate usage of the emulator.
 
 * ``addresses`` - Addresses in the emulated "wallet" that are owned by the emulated daemon
 
 * ``external_addresses`` - External/foreign addresses (i.e. not controlled by this wallet). Used for very basic
   address validation.
 
 * ``getblockchaininfo`` - Stores the dictionary that would be returned by a :func:`.getblockchaininfo` call
 
 * ``getnetworkinfo`` - Stores the dictionary that would be returned by a :func:`.getnetworkinfo` call
 

"""

fake = Faker()
"""An instance of :class:`faker.Faker` for generating fake data in functions such as :func:`.j_gen_tx`"""


def j_gen_tx(account="", address=None, amount=None, category=None, **kwargs):
    """
    Generate a Bitcoin transaction and return it as a dict.
    
    If any transaction attributes aren't specified, fake data will be automatically generated using :py:mod:`random` or
    :py:mod:`faker` to fill the attributes.
    
    :param account: Wallet account to label the transaction under
    :param address: **Our** address, that we're sending from or receiving into.
    :param amount: The amount of BTC transferred
    :param category: Either ``'receive'`` or ``'send'``
    :param kwargs: Any additional dict keys to put into the TX data
    :return dict tx: The generated TX
    """
    address = random.choice(internal["addresses"]) if address is None else address
    category = random.choice(['receive', 'send']) if category is None else category
    amount = Decimal(random.random(), 7) if amount is None else Decimal(amount)
    amount = dec_round(amount, dp=8)
    # If an amount is being sent, then the amount becomes negative.
    # If an amount is being received, the amount must be positive.
    if (category == 'send' and amount > 0) or (category == 'receive' and amount < 0):
        amount = -amount
    
    tx = dict(
        account=account,
        address=address,
        amount=amount,
        category=category,
    )
    tx = {**tx, **kwargs}
    
    tx['txid'] = tx.get('txid', fake.sha256())
    tx['confirmations'] = tx.get('confirmations', random.randint(1, 30))
    
    if 'time' not in tx:
        tx['time'] = int(fake.unix_time(start_datetime=datetime.utcnow() - timedelta(days=5)))
    
    tx['label'] = tx.get('label', '')
    tx['vout'] = tx.get('vout', 0)
    tx['generated'] = is_true(tx.get('generated', False))
    
    return tx


def j_add_tx(account="", address = None, amount: Union[float, str, Decimal] = None, category: str = None, **kwargs):
    """
    Generate a transaction using :py:func:`.j_gen_tx` using the passed arguments, then store it into the
    transaction list.
    
    :param account: Wallet account to label the transaction under
    :param address: **Our** address, that we're sending from or receiving into.
    :param amount: The amount of BTC transferred
    :param category: Either ``'receive'`` or ``'send'``
    :param kwargs: Any additional dict keys to put into the TX data
    :return dict tx: The generated TX
    """
    tx = j_gen_tx(
        account=account, address=address, amount=amount, category=category, **kwargs
    )
    internal['transactions'].append(tx)
    return tx


def j_update_blockchaininfo(**kwargs):
    """Update keys in the blockchaininfo using the kwargs"""
    internal['getblockchaininfo'] = {**internal['getblockchaininfo'], **kwargs}
    return internal['getblockchaininfo']


def j_update_networkinfo(**kwargs):
    """Update keys in the networkinfo using the kwargs"""
    internal['getnetworkinfo'] = {**internal['getnetworkinfo'], **kwargs}
    return internal['getnetworkinfo']


def j_transactions(cast_decimal=float) -> List[dict]:
    """
    Returns ``internal['transactions']`` with unserializable types such as ``Decimal`` casted appropriately.
    
    This should be used instead of ``internal['transactions']`` if returning TXs from the RPC.
    
    :param cast_decimal: A casting function to use to convert Decimal's, e.g. ``float`` or ``str``
    :return List[dict] txs: A list of dict transactions, with values converted to allow JSON serialisation.
    """
    new_txs = []
    for tx in internal['transactions']:
        new_tx = {}
        for k, v in tx.items():
            if type(v) is Decimal:
                new_tx[k] = cast_decimal(v)
                continue
            new_tx[k] = v
        new_txs.append(new_tx)
    return new_txs


def _address_valid(address: str):
    if address in internal['addresses']:
        return True
    if address in internal['external_addresses']:
        return True
    return False


def _address_balances() -> List[Tuple[str, Decimal]]:
    """
    Calculate the balance for each address in ``internal['addresses']`` based on
    stored transactions.
    """
    balances = {}
    for tx in internal['transactions']:
        addr = tx['address']
        if addr not in internal['addresses']:
            continue
        if addr not in balances:
            balances[addr] = Decimal(0)
        balances[addr] += Decimal(tx['amount'])
    
    return sorted(balances.items(), key=lambda d: d[1], reverse=True)


def _get_balance(account="*", confirmations: int = 0):
    """Internal function for calculating balances"""
    total = Decimal(0)
    # Send transactions have negative amounts, while receive transactions have positive amounts
    # so we don't need to differentiate them, just add them to the total.
    for tx in internal['transactions']:  # type: dict
        if account not in ['', '*', None]:
            if tx['account'].lower() != account.lower():
                continue
        if tx['confirmations'] < confirmations:
            continue
        total += Decimal(tx['amount'])
    return total


@method
def getbalance(account="*", confirmations: int = 0, watch_only=False):
    """
    Get the balance of the RPC node, or an individual account.
    
    :param str account: Only get the balance for this account. ``"*"`` or ``""`` will sum all accounts.
    :param str confirmations: Only include transactions with at least this many confirmations
    :param watch_only: NOT IMPLEMENTED
    :return float balance: The total balance as a float
    """
    return float(_get_balance(account, confirmations))


@method
def listtransactions(account="*", count: int = 10, skip: int = 0, watch_only=False):
    """
    Simulates a Bitcoin RPC ``listtransactions`` call - returns a list of dictionary transactions
    from :py:attr:`.internal` ``['transactions']``


    :param account: Account to list TXs for
    :param count: Load this many recent TXs
    :param skip: Skip this many recent TXs (for pagination)
    :param watch_only: (NOT IMPLEMENTED)
    :return: [ {account, address, category, amount, label, vout, fee, confirmations, trusted, generated,
                txid, time, comment, to}, ... ]

    """
    tx_list = j_transactions()
    if account in ['', '*', None]:
        return tx_list[skip:count]
    _txs = []
    for tx in tx_list:
        if tx.get('account', '').lower() == account.lower():
            _txs.append(tx)
    
    return _txs


@method
def getblockchaininfo():
    """Return bitcoind blockchain information, e.g. current block height"""
    return internal['getblockchaininfo']


@method
def getnetworkinfo():
    """Return bitcoind network information, e.g. coin daemon version"""
    return internal['getnetworkinfo']


@method
def getnewaddress(account="", address_type=None):
    """
    Generate a Bitcoin address. Note: this is simulated, it just pulls a random address from ``internal['addresses']``
    """
    return random.choice(internal["addresses"])


@method
def getreceivedbyaddress(address, confirmations: int = 0):
    """Returns the total amount of coins received by ``address`` (excludes send transactions!)"""
    total = Decimal(0)
    for tx in internal['transactions']:  # type: dict
        if tx['category'] != 'receive': continue
        if tx['confirmations'] < confirmations: continue
        if tx['address'] != address: continue
        total += Decimal(tx['amount'])
    
    return float(total)


@method
def sendtoaddress(address, amount: Union[float, str, Decimal], comment="", comment_to="", subtractfee: bool = False):
    """
    Sends ``amount`` BTC to ``address`` - generates a fake TX in :py:attr:`.internal` transaction storage.
    
    Example::

        $ curl -v -s --data '{"method": "sendtoaddress",
            "params": ["1J2VishkhGviaEZA5dYgrqW1bjV8JGKFj", "0.001", "", "", false],
            "jsonrpc": "2.0", "id": 1}' http://127.0.0.1:5000

        {"jsonrpc": "2.0", "result": "a4415c4013d2ba58106795ecb36a8694a3e93a4056e39ace4adde80d083c9641", "id": 1}


    :param address: The destination Bitcoin address
    :param amount: The amount to send to ``address``
    :param str comment:     A comment used to store what the transaction is for.
    :param str comment_to:  A comment, representing the name of the person or organization you're sending to.
    :param bool subtractfee: (Default False) If set to True, reduce the sending amount to cover the TX fee.
    :return:
    """
    log.debug('Checking if address %s is valid', address)
    assert _address_valid(address), "Invalid address"
    log.debug('Converting amount %s to decimal', amount)
    amount = Decimal(amount)
    log.debug('Checking amount %s is > 0.00000001', amount)
    assert amount > Decimal('0.00000001'), "Invalid amount"
    log.debug('Checking if we have enough balance')
    assert amount < Decimal(_get_balance()), "Insufficient funds"
    log.debug('Getting best address to send from')
    best_addr, bal = _address_balances()[0]
    log.debug('Best address: %s    Balance: %s', best_addr, bal)
    assert bal > amount, "Insufficient funds (Emulation limitation - can only send from one address)"
    log.debug('Generating SEND transaction')
    
    tx = j_add_tx(
        address=best_addr, amount=amount, category="send", comment=comment, comment_to=comment_to,
        label=f"Sent from {best_addr} to {address}",
    )
    log.debug('Checking if internal address')
    if address in internal['addresses']:
        log.debug('Generating RECEIVE transaction')
        j_add_tx(address=address, amount=amount, category="receive", comment=comment, comment_to=comment_to,
                 label=f"Sent from {best_addr} to {address}", txid=tx['txid'])
    log.debug('Returning TXID')
    
    return tx['txid']


class BitcoinEmulator(Emulator):
    """
    Process manager class for the ``bitcoind`` emulator web server.
    
    Without any constructor arguments, will fork into background at http://127.0.0.1:8332

    By default, ``background`` is set to True, meaning it will launch as a sub-process, instead of blocking
    your application.

    **Using with a Context Manager**::

    By using :class:`.BitcoinEmulator` as a context manager, the JsonRPC server will be started before the first line
    inside of the ``with`` statement, and will automatically shutdown at the end of the ``with`` statement.

        >>> from privex.rpcemulator.bitcoin import BitcoinEmulator
        >>>
        >>> with BitcoinEmulator():
        ...     # make some queries to the RPC at https://127.0.0.1:8332
        ...
        >>> # Once the `with` statement is over, the JsonRPC server automatically shuts down

    **Alternative**
    
    You can create an instance of BitcoinEmulator normally, but you should make sure to call :py:meth:`.terminate`
    when you're done with using the emulator.
    
    This may be preferable when using inside of a unit test which has a setUpClass and tearDownClass method::

        >>> from privex.rpcemulator.bitcoin import BitcoinEmulator
        >>> btc_rpc = BitcoinEmulator()
        >>> # make some queries to the RPC at https://127.0.0.1:8332
        >>> # once you're done, terminate the process
        >>> btc_rpc.terminate()
    
    """
    
    def __init__(self, host="", port: int = 8332, background=True):
        """
        Without any constructor arguments, will fork into background at http://127.0.0.1:8332

        By default, ``background`` is set to True, meaning it will launch as a sub-process, instead of blocking
        your application.
        
        
            >>> from privex.rpcemulator.bitcoin import BitcoinEmulator
            >>>
            >>> with BitcoinEmulator():
            ...     # make some queries to the RPC at https://127.0.0.1:8332
            ...
            >>> # Once the `with` statement is over, the JsonRPC server automatically shuts down


        :param str host: The IP address to listen on. If left as ``""`` - will listen at 127.0.0.1
        :param int port: The port number to listen on (Defaults to 8332, same as Bitcoin)
        :param bool background: If ``True``, spawns the webserver in a sub-process, instead of blocking the app.
        """
        super().__init__(host=host, port=port, background=background)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    def __del__(self):
        super().__del__()



