import aiohttp
from .http import HttpHandler

class Client:
    """
    Base pyvolt client.

    Attributes:
        client: aiohttp.ClientSession
            The aiohttp client session.
        http: pyvolt.HttpHandler  
            The http handler.
        ws: pyvolt.WebSocketHandler
            The websocket handler.
        listeners: dict
            A dictionary of listeners.
    """
    def __init__(self):
        self.client = aiohttp.ClientSession()
        self.http = HttpHandler()
        self.ws = None
        self.listeners = {}