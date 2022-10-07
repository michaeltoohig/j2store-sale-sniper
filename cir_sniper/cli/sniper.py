import pickle
from cir_sniper.loggerfactory import LoggerFactory
from cir_sniper.sniper.session import SniperSession
from cir_sniper.sniper.market import Market, MarketItem
from cir_sniper.sniper.cart import Cart
from cir_sniper.sniper.utils import check_response__sale_closed, fetch_sale_start_page
from cir_sniper.config import BASE_URL, WISHLIST_FILE

import click
import requests
from bs4 import BeautifulSoup
from tenacity import Retrying, wait_random, retry_if_result, before_log, retry_if_exception_type

logger = LoggerFactory.get_logger("sniper")


@click.group()
@click.pass_context
def sniper(ctx):
    pass


@sniper.command()
def sale_status():
    """Check if sale is open to public."""
    resp = fetch_sale_start_page()
    status = "closed" if check_response__sale_closed(resp) else "open"
    click.echo(f"Sale Status: {status}")


@sniper.command()
@click.option("--no-login", is_flag=True, default=False, help="Do not login")
@click.option("--export-market-items", is_flag=True, default=False, help="Pickle market items")
def run(no_login, export_market_items):
    """Run sale sniper."""
    # Check wishlist
    if not WISHLIST_FILE.exists():
        click.echo("No wishlist file")
        raise click.Abort()
    # Check sale is open
    retryer = Retrying(
        wait=wait_random(min=5, max=10),
        retry=(retry_if_result(check_response__sale_closed) | retry_if_exception_type()),
        before=before_log(logger, 10),
    )
    retryer(fetch_sale_start_page)
    logger.info("Sale Confirmed Open")
    # Setup Sniper
    session = SniperSession()
    market = Market(session)
    cart = Cart(session)
    if not no_login:
        cart.login()
    # Get Market Catalog
    market.get_items()
    if export_market_items:
        market.export_items()
    # Get Wishlist Items
    with WISHLIST_FILE.open("rb") as f:
        wishlist_items = pickle.load(f)
    # Add Wishlist Items to Cart
    for lot_number in map(lambda wi: wi.lot, wishlist_items):
        if lot_number not in market:
            click.echo(f"Market does not have wishlist item lot={lot_number}")
            continue
        item = market[lot_number]
        cart.add_market_item(item)
    cart.get_items()

    # Confirm Purchase
    click.echo("your cookies for manual login")
    click.echo(session.cookies.get_dict())
    click.echo(cart)
    if not no_login:
        # If logged in then checkout can be performed
        if click.confirm("Continue checkout"):
            cart.checkout()
            click.echo("Checkout Completed")


@sniper.command()
def run_checkout():
    """Run checkout steps only."""
    # Setup Sniper
    session = SniperSession()
    cart = Cart(session)
    cart.login()
    cart.get_items()

    # Confirm Purchase
    click.echo("your cookies for manual login")
    click.echo(session.cookies.get_dict())
    click.echo(cart)
    if click.confirm("Continue checkout"):
        cart.checkout()
        click.echo("Checkout Completed")


@sniper.command()
def fetch_full_inventory():
    """Fetch J2Store inventory listing page and parse market items.
    Results can be different than the actual paginated results from the `Market` class.
    Use for curiosity only.
    """
    resp = requests.get(f"{BASE_URL}/component/j2store/sale")
    soup = BeautifulSoup(resp.text, "html.parser")
    mainbody = soup.find("div", {"id": "t3-mainbody"})
    items = mainbody.find_all("div", {"class": "j2store-single-product"})

    def parse_item_tag(tag) -> MarketItem:
        name = tag.h2.text.strip()
        description = tag.find("div", {"class": "product-short-description"}).text.strip()
        unit_price = int(
            tag.find("div", {"class": "sale-price"}).text.strip().lower().replace("vt", "").replace(",", "")
        )
        src = None
        stock_tag = tag.find("div", {"class": "product-stock-container"})
        try:
            in_stock = "instock" in stock_tag.span.attrs.get("class")
        except AttributeError:
            in_stock = False
        inputs = tag.form.find_all("input")
        form_data = {i.attrs["name"]: i.attrs["value"] for i in inputs if i.attrs.get("name", False)}
        return MarketItem(
            id=int(tag.form.attrs.get("data-product_id")),
            lot=name.split()[1],
            name=name,
            description=description,
            unit_price=unit_price,
            src=src,
            in_stock=in_stock,
            form_data=form_data,
        )

    market_items = []
    for item in items:
        market_items.append(parse_item_tag(item))
    click.echo("You should drop into interactive mode here to explore `market_items`")
    import pdb

    pdb.set_trace()
