import pickle
from cir_sniper.loggerfactory import LoggerFactory
from cir_sniper.sniper.session import SniperSession
from cir_sniper.sniper.market import Market
from cir_sniper.sniper.cart import Cart
from cir_sniper.sniper.utils import check_response__sale_closed, fetch_sale_start_page
from cir_sniper.config import WISHLIST_FILE

import click
from tenacity import Retrying, wait_random, retry_if_result, before_log, retry_if_exception_type

logger = LoggerFactory.get_logger("sniper")


@click.group()
@click.pass_context
def sniper(ctx):
    pass


@sniper.command()
def run():
    """Run sale sniper."""
    # TODO login flag default yes
    login = False
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
    if login:
        cart.login()
    # Get Market Catalog
    market.get_items()
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
    if click.confirm("Continue checkout"):
        cart.checkout()
        click.echo("Checkout Completed")


@sniper.command()
def sale_status():
    resp = fetch_sale_start_page()
    status = "closed" if check_response__sale_closed(resp) else "open"
    click.echo(f"Sale Status: {status}")
