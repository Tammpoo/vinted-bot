from .VintedItem import VintedItem
from .requester import requester
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json


class VintedItems:
    def __init__(self):
        pass

    def search(self, url, nbr_items=20):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params["per_page"] = [str(nbr_items)]

        new_query = urlencode(query_params, doseq=True)
        search_url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                "/api/v2/catalog/items",
                "",
                new_query,
                "",
            )
        )

        response = requester.get(search_url)
        if response.status_code != 200:
            return []

        data = response.json()
        items_data = data.get("items", [])
        items = [VintedItem(item) for item in items_data]
        return items
