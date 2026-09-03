import click

from .sync import run_sync


@click.group()
def main():
    """Banking - Plain-text accounting CLI toolchain."""
    pass


@main.command()
@click.option("--refresh", is_flag=True, help="Bypass cache and fetch fresh data")
def sync(refresh: bool):
    """Synchronize transactions from bank feeds into journals."""

    run_sync(use_cache=not refresh)


if __name__ == "__main__":
    main()
