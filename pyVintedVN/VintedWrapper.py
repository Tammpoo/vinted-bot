import requests
from .requester import requester


class VintedWrapper:
    def __init__(self, base_url="https://www.vinted.it"):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        return requester.get(url, params=params)
