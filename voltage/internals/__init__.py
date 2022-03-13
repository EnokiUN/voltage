"""
The Voltage internal library, aka where the magic happens.

You probably shouldn't be using this directly, but rather through the client unless you're curios or are helping out developing Voltage.
"""

from .cache import CacheHandler
from .http import HTTPHandler
from .ws import WebSocketHandler
