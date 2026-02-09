import requests
from config import *

def fetch_stock():
    if not STOCK_CHECK_ENABLED:
        return None

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    params = {
        "url": SHEIN_VERSE_URL
    }

    r = requests.get(
        RAPIDAPI_URL,
        headers=headers,
        params=params,
        timeout=20
    )
    r.raise_for_status()

    return r.json()
