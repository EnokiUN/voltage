from asyncio import get_running_loop
from typing import Optional, Dict

# Internal imports
from .http import HTTPHandler

class CacheHandler:
    def __init__(self, http: HTTPHandler, message_limit: Optional[int] = 5000):
        self.http = http
        self.message_limit = message_limit
        self.loop = get_running_loop()

        self.users = {}