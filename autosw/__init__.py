import logging
from .commands import operate
from .api import app

logging.basicConfig(level=logging.DEBUG)

__version__ = "0.1.2"
