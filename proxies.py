import random
import db
from logger import get_logger

logger = get_logger(__name__)


def get_proxy():
    proxies_str = db.get_parameter("proxies")
    if not proxies_str:
        return None

    proxies = [p.strip() for p in proxies_str.split("\n") if p.strip()]
    if not proxies:
        return None

    proxy = random.choice(proxies)
    return {"http": proxy, "https": proxy}
