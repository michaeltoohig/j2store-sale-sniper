from cir_sniper.config import BASE_URL
from cir_sniper.loggerfactory import LoggerFactory

import requests
from bs4 import BeautifulSoup

logger = LoggerFactory.get_logger("sniper.utils")


def check_response__sale_closed(resp):
    soup = BeautifulSoup(resp.text, "html.parser")
    return "sale is now closed" in soup.find("div", {"class": "t3-content"}).text.lower()


def fetch_sale_start_page():
    resp = requests.get(f"{BASE_URL}/customs/customs-sale")
    return resp
