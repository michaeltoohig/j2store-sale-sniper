from pathlib import Path
import pickle
from dataclasses import dataclass

from cir_sniper.cli.utils import print_table
from cir_sniper.config import WISHLIST_FILE
from cir_sniper.loggerfactory import LoggerFactory

import click

logger = LoggerFactory.get_logger("wishlist")


@dataclass
class WishlistItem:
    lot: int
    description: str
    qty: int = 1


@click.group()
@click.pass_context
def wishlist(ctx):
    pass


@wishlist.command()
@print_table
def show():
    if not WISHLIST_FILE.exists():
        click.echo("No Wishlist Items")
        raise click.Abort()
    with WISHLIST_FILE.open("rb") as f:
        items = pickle.load(f)
    return [
        (
            i.lot,
            i.description,
            i.qty,
        )
        for i in items
    ]


@wishlist.command()
@click.option("--lot", type=click.INT, prompt=True)
@click.option("--description", prompt=True)
@click.option("--qty", type=click.INT, required=True, default=1)
def add(lot, description, qty):
    item = WishlistItem(lot, description, qty)
    items = []
    if WISHLIST_FILE.exists():
        with WISHLIST_FILE.open("rb") as f:
            items = pickle.load(f)
    items.append(item)
    with WISHLIST_FILE.open("wb") as f:
        pickle.dump(items, f)


@wishlist.command()
def clear():
    if click.confirm("Clear wishlist file?"):
        if WISHLIST_FILE.exists():
            WISHLIST_FILE.unlink()
