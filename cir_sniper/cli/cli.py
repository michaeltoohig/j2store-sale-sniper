import click

from .sniper import sniper as sniper_cli
from .wishlist import wishlist as wishlist_cli


@click.group()
@click.version_option()
def cli():
    "A bespoke J2Store sale sniper."


cli.add_command(sniper_cli)
cli.add_command(wishlist_cli)
