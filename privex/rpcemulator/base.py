import multiprocessing
import warnings
from http.server import HTTPServer
from os.path import dirname, abspath
from typing import Optional

from jsonrpcserver import serve
from jsonrpcserver.server import RequestHandler
import logging

log = logging.getLogger(__name__)

BASE_DIR = dirname(dirname(dirname(abspath(__file__))))


class QuietRequestHandler(RequestHandler):
    """
    Same as :class:`jsonrpcserver.server.RequestHandler` but with logging disabled.
    """
    def log_message(self, format, *args):
        return


def quiet_serve(name: str = "", port: int = 5000) -> None:
    """
    Quiet version of :py:func:`jsonrpcserver.serve` with logging disabled.

    Args:
        name: Server address.
        port: Server port.
    """
    log.info(" * Listening on port %s", port)
    httpd = HTTPServer((name, port), QuietRequestHandler)
    httpd.serve_forever()


def _serve(host="", port=5000, quiet=False, use_coverage=False):
    """
    Wrapper function for :func:`jsonrpcserver.serve` and :func:`.quiet_serve`. Can be forked into background.
    
    Sets up SIGTERM hook using :py:func:`pytest_cov.embed.cleanup_on_sigterm` so coverage data is correctly
    saved when the subprocess is terminated.
    """
    # If this is being called from a unit test, then attempt to setup the pytest-cov SIGTERM hook to ensure
    # coverage data is generated correctly for this subprocess.
    if use_coverage:
        try:
            from pytest_cov.embed import cleanup_on_sigterm
            cleanup_on_sigterm()
        except ImportError:
            warnings.warn("Could not import coverage module in child process...")
            pass
    srv = quiet_serve if quiet else serve
    srv(host, port)


class Emulator:
    """
    This is the base class used by JsonRPC emulators such as :class:`privex.rpcemulator.bitcoin.BitcoinEmulator`
    
    It fires :py:func:`jsonrpcserver.serve` into the background using :py:mod:`multiprocessing` and handles
    shutting down the process either via context management (``with`` statements), direct calls to
    :py:meth:`.terminate`, or when the object is garbage collected via :py:meth:`.__del__`
    
    """
    proc: Optional[multiprocessing.Process]
    """Holds the :class:`multiprocessing.Process` background process instance for serve()"""
    
    quiet = False
    """Set ``Emulator.quiet = True`` to use :py:func:`.quiet_serve` (disable HTTP request logging)"""
    
    use_coverage = False
    """When running unit tests, this should be set to True to load coverage in the subprocess"""
    
    def __init__(self, host="", port: int = 5000, background=True):
        """
        Launch an RPC emulator web server. Without arguments, will fork into background at http://127.0.0.1:5000

        By default, ``background`` is set to True, meaning it will launch as a sub-process, instead of blocking
        your application. You can use the returned :class:`multiprocessing.Process` object to terminate it once
        you're done using it.

        **Using with a Context Manager**::
            >>> from privex.rpcemulator.base import Emulator
            >>>
            >>> with Emulator():
            ...     # make some queries to the RPC at https://127.0.0.1:5000
            ...
            >>> # Once the `with` statement is over, the JsonRPC server automatically shuts down
        
        Example::

            >>> from privex.rpcemulator.base import Emulator
            >>> rpc = Emulator()
            >>> # make some queries to the RPC at https://127.0.0.1:5000
            >>> # once you're done, terminate the process
            >>> rpc.terminate()

        :param str host: The IP address to listen on. If left as ``""`` - will listen at 127.0.0.1
        :param int port: The port number to listen on (Defaults to 5000)
        :param bool background: If ``True``, spawns the webserver in a sub-process, instead of blocking the app.
        """
        
        if not background:
            _serve(host, port)
            return
        t = multiprocessing.Process(target=_serve, args=(host, port, self.quiet, self.use_coverage))
        t.daemon = True
        t.start()
        self.proc = t

    def terminate(self):
        """
        Called when a user wants to manually terminate the background process.
        
        Simply calls :py:meth:`.__del__` to terminate the process.
        """
        self.__del__()
    
    def __enter__(self):
        """Called at the start of a ``with`` statement for context management"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        When a ``with`` statement has ended, calls :py:meth:`.__del__` to terminate the process.
        """
        self.__del__()
    
    def __del__(self):
        """
        Cleanup by terminating the background process if it's still running.
        
        When the instance is garbage collected, or ``del someinstance`` is called, this method should get triggered.
        """
        if self.proc is not None and self.proc.is_alive():
            self.proc.terminate()
        self.proc = None
