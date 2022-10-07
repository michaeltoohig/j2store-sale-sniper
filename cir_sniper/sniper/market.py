import pickle
from dataclasses import dataclass, asdict
from typing import Dict

from cir_sniper.config import BASE_URL, MARKET_ITEMS_PER_PAGE, MOCK_MARKET_ITEMS_FILE
from cir_sniper.loggerfactory import LoggerFactory
from cir_sniper.sniper.session import SniperSession

from bs4 import BeautifulSoup
from bs4.element import Tag
from tabulate import tabulate

logger = LoggerFactory.get_logger("sniper.market")


@dataclass
class MarketItem:
    """A market item."""

    id: int
    lot: int
    name: str
    description: str
    unit_price: int
    src: str  # URL type?
    in_stock: bool
    form_data: dict


class Market:
    MARKET_URL = f"{BASE_URL}/customs-online-sale"
    items: Dict[int, MarketItem] = None
    items_per_page = MARKET_ITEMS_PER_PAGE

    def __init__(self, session: SniperSession):
        self.session = session
        self.items = {}

    def __str__(self):
        data = [(i.lot, i.description, i.unit_price, i.in_stock) for i in self.items.values()]
        return tabulate(data)

    def __contains__(self, lot: int):
        """Checks if the human readable `lot number` exists in the market."""
        return lot in map(lambda i: i.lot, self.items.values())

    def __getitem__(self, lot: int):
        """Returns MarketItem by the human readable `lot number`."""
        return next(filter(lambda i: i.lot == lot, self.items.values()), None)

    def parse_item_tag(self, tag: Tag) -> MarketItem:
        name = tag.find("header").find("a").text.strip()
        description = tag.find("section").find("p").text.strip()
        unit_price = int(
            tag.find("section")
            .find("div", {"class": "sale-price"})
            .text.strip()
            .lower()
            .replace("vt", "")
            .replace(",", "")
        )
        src = tag.find("article").find("img")["src"]
        in_stock = tag.find("section").find("span", {"class": "outofstock"}) is None
        inputs = tag.find("section").find("form").find_all("input")
        inputs = filter(lambda i: i.attrs["type"] not in ["button", "submit"], inputs)
        form_data = {i.attrs["name"]: i.attrs["value"] for i in inputs}
        return MarketItem(
            id=int(form_data.get("product_id")) if in_stock else None,
            lot=int(name.split()[1]),  # HACK Assumes name `LOT X - XYZA` pattern
            name=name,
            description=description,
            unit_price=unit_price,
            src=src,
            in_stock=in_stock,
            form_data=form_data,
        )

    def get_page(self, *, start: int) -> Tag:
        """Fetch a single page."""
        logger.debug(f"Get market page start={start}")
        resp = self.session.get(self.MARKET_URL, params=dict(start=start))
        return BeautifulSoup(resp.text, "html.parser")

    def get_items(self) -> None:
        """Fetch all items in the market."""
        page = 0
        while True:
            soup = self.get_page(start=page * self.items_per_page)
            page += 1
            # Check for empty results
            if "there are no articles in this category." in soup.body.text.lower():
                break
            item_tags = soup.find("div", {"class": "t3-content"}).find_all("div", {"class": "item"})
            for item_tag in item_tags:
                market_item = self.parse_item_tag(item_tag)
                self.add_market_item(market_item)

    def add_market_item(self, i: MarketItem) -> None:
        logger.debug(f"Add market item id={i.id} lot={i.lot}")
        self.items[i.id] = i

    def export_items(self):
        """Export to pickle for use in `mock_j2store`."""
        logger.debug("Exporting market items")
        with MOCK_MARKET_ITEMS_FILE.open("wb") as f:
            pickle.dump([asdict(i) for i in self.items.values()], f)
