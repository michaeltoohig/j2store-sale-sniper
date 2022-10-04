import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
BASE_URL = os.environ.get("BASE_URL")

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

WISHLIST_FILE = Path(os.environ.get("WISHLIST_FILE", "wishlist.pkl"))
MOCK_MARKET_ITEMS_FILE = Path(os.environ.get("MOCK_MARKET_ITEMS_FILE", "market-items.pkl"))

REQUEST_SESSION_KEEP = os.environ.get("REQUEST_SESSION_KEEP", False)
REQUEST_SESSION_DATA_DIRECTORY = os.environ.get("REQUEST_SESSION_DATA_DIRECTORY", "log/sessions")
MARKET_ITEMS_PER_PAGE = os.environ.get("MARKET_ITEMS_PER_PAGE", 24)  # static
