from dataclasses import dataclass
from typing import List

from cir_sniper.config import BASE_URL, PASSWORD, USERNAME

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from tabulate import tabulate

from cir_sniper.sniper.session import SniperSession
from cir_sniper.sniper.market import MarketItem
from cir_sniper.loggerfactory import LoggerFactory

logger = LoggerFactory.get_logger("sniper.cart")


@dataclass
class CartItem:
    """A cart item."""

    id: int
    name: str
    quantity: int
    unit_price: int

    def subtotal(self):
        return self.unit_price * self.quantity


class Cart:
    CART_URL = f"{BASE_URL}/component/j2store/carts"
    logged_in: bool = False
    items: List[CartItem] = None

    def __init__(self, session: SniperSession):
        self.session = session

    def __str__(self):
        if not self.items:
            return "Empty Cart"
        data = [(i.id, i.name, i.quantity, i.subtotal()) for i in self.items]
        data.append((None, None, None, self.total()))
        return tabulate(data)

    def __getitem__(self, cartitem_id: int):
        """Returns CartItem by the `id`."""
        return next(filter(lambda i: i.id == cartitem_id, self.items.values()), None)

    def total(self) -> int:
        return sum([i.subtotal() for i in self.items])

    def _get_text(self, tag: Tag) -> str:
        return "".join(tag.find_all(text=True, recursive=False)).strip()

    def _parse_cart_row(self, tag: Tag) -> CartItem:
        name = self._get_text(tag.find("span", {"class": "cart-product-name"}))
        quantity = tag.find("input").attrs["value"]
        unit_price = (
            tag.find("span", {"class": "cart-item-value"}).text.strip().lower().replace(",", "").replace("vt", "")
        )
        remove_link = tag.find("a", {"class": "remove-icon"})["href"]
        query_args = dict(q.split("=") for q in requests.utils.urlparse(remove_link).query.split("&"))
        return CartItem(
            id=query_args.get("cartitem_id"),
            name=name,
            quantity=int(quantity),
            unit_price=int(unit_price),
        )

    def get_items(self):
        resp = self.session.get(self.CART_URL)
        soup = BeautifulSoup(resp.text, "html.parser")
        content = soup.find("div", {"id": "t3-content"})
        self.items = []
        if "no items found in the cart" in content.text.lower():
            logger.info("Cart is Empty")
            return
        row_tags = content.find("form").find("table").find("tbody").find_all("tr")
        for row_tag in row_tags:
            item = self._parse_cart_row(row_tag)
            self.items.append(item)

    def change_item_quantity(self, i: CartItem, qty: int) -> None:
        logger.debug(f"Changing quantity in cart lot={i.lot} qty={qty}")
        form_data = {
            "option": "com_j2store",
            "ajax": "1",
            "view": "carts",
            "task": "update",
            f"quantities[{i.id}]": qty,
        }
        self.session.post(self.CART_URL, data=form_data)
        i.quantity = qty

    def remove_item(self, i: CartItem) -> None:
        logger.debug(f"Removing from cart lot={i.lot}")
        params = {"cartitem_id": i.id}
        self.session.get(f"{self.CART_URL}/remove", params=params)
        self.items = list(filter(lambda item: item.id != i.id, self.items))

    def add_market_item(self, item: MarketItem) -> None:
        # form_data comes from the MarketItem object
        logger.debug(f"Adding to cart lot={item.lot}")
        self.session.post(f"{self.CART_URL}/addItem", data=item.form_data)

    def login(self):
        login_form_data = {
            "email": USERNAME,
            "password": PASSWORD,
            "task": "login_validate",
            "option": "com_j2store",
            "view": "checkout",
        }
        resp = self.session.post(self.CART_URL, data=login_form_data)
        self.session.update_cookies(resp.cookies)
        logger.info(f"Logged in as {USERNAME}")

    def checkout(self, customer_note: str = ""):
        get_existing_address_form_data = {
            "option": "com_j2store",
            "view": "checkout",
            "task": "billing_address",
        }
        resp = self.session.post(self.CART_URL, data=get_existing_address_form_data)
        soup = BeautifulSoup(resp.text)
        address_id = soup.find("div", {"id": "billing-existing"}).option.attrs["value"]
        country_id = soup.find("select", {"name": "country_id"}).option.attrs["value"]
        inputs = soup.find_all("input")
        validate_billing_address_form_data = {i.get("name"): i.get("value") for i in inputs if i.get("name", False)}
        validate_billing_address_form_data["country_id"] = country_id
        validate_billing_address_form_data["address_id"] = address_id
        self.session.post(self.CART_URL, data=validate_billing_address_form_data)
        get_payment_methods_form_data = {
            "option": "com_j2store",
            "view": "checkout",
            "task": "shipping_payment_method",
        }
        self.session.post(self.CART_URL, data=get_payment_methods_form_data)
        validate_payment_method_form_data = {
            "payment_plugin": "payment_cash",
            "customer_note": customer_note,
            "task": "shipping_payment_method_validate",
            "option": "com_j2store",
            "view": "checkout",
        }
        self.session.post(self.CART_URL, data=validate_payment_method_form_data)
        get_confirm_form_data = {
            "option": "com_j2store",
            "view": "checkout",
            "task": "confirm",
        }
        resp = self.session.post(self.CART_URL, data=get_confirm_form_data)
        soup = BeautifulSoup(resp.text, "html.parser")
        inputs = soup.find("form", {"id": "cash_form"})
        validate_confirm_payment_form_data = {i.get("name"): i.get("value") for i in inputs if i.get("name", False)}
        self.session.post(self.CART_URL, data=validate_confirm_payment_form_data)
        logger.info("Purchase complete :)")
