import click

from banking.reset import clear_bank_journals

from .reset import clear_bank_journals, clear_cache, clear_sync_state
from .sync import run_sync


@click.group()
def main():
    """Banking - Plain-text accounting CLI toolchain."""


@main.command()
@click.option("--refresh", is_flag=True, help="Bypass cache and fetch fresh data")
def sync(refresh: bool):
    """Synchronize transactions from bank feeds into journals."""

    run_sync(use_cache=not refresh)


@main.command()
@click.option("--cache", is_flag=True, help="Clear the account caches only.")
@click.option("--hard", is_flag=True, help="Wipe all journals, state and cache files.")
def reset(cache: bool, hard: bool):
    """Reset local transaction and state files"""

    if hard:
        confirmed = click.confirm(
            "This will delete ALL local transaction files,"
            "including cache and sync_state."
        )

        if not confirmed:
            click.echo("Aborted.")
            return

        clear_bank_journals()
        clear_sync_state()
        clear_cache()
        click.echo("All transaction files deleted. System has been reset.")

    elif cache:
        clear_cache()
        click.echo("Cache reset.")

    else:
        clear_sync_state()
        clear_bank_journals()
        click.echo(
            "Journals and state reset. Opening balances and cache are unchanged."
        )


if __name__ == "__main__":
    main()
