from .requester import requester


class VintedItem:
    def __init__(self, data):
        self.raw_data = data
        self.id = data.get("id")
        self.title = data.get("title", "")
        self.price = data.get("price", {}).get("amount", "N/A")
        self.currency = data.get("price", {}).get("currency", "")
        self.brand_title = data.get("brand_title", "")
        self.photo = data.get("photo", {}).get("url", None) if data.get("photo") else None
        self.url = data.get("url", "")
        self.raw_timestamp = data.get("photo", {}).get("high_resolution", {}).get("timestamp", 0) if data.get("photo") and data.get("photo").get("high_resolution") else 0
        if not self.raw_timestamp:
            self.raw_timestamp = data.get("created_at_ts", 0)

    def is_new_item(self):
        return True
