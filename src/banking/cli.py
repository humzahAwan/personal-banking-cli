import click

from .balances import get_balances, set_opening_balance
from .banner import print_banner, print_system_diagnostic
from .reset import clear_bank_journals, clear_cache, clear_sync_state
from .scheduler import check_status, install_schedule, remove_schedule
from .setup import run_setup
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


@main.group(name="opening-balances")
def opening_balances():
    """Manage opening balances."""


@opening_balances.command(name="list")
def list_cmd():
    """List opening balances."""
    balances = get_balances()

    click.echo(f"{'DATE':<12} {'ACCOUNT':<38} {'AMOUNT':>10}")
    click.echo("-" * 62)

    for b in balances:
        click.echo(f"{b.date:<12} {b.account:<38} {b.amount:>}")


@opening_balances.command(name="set")
@click.argument("account", type=str, help="Account Number eg. assets:bank:home")
@click.argument("amount", type=float, help="Opening amount. Excluding currency symbol")
@click.option(
    "--date", default=None, help="Transaction date (YYYY-MM-DD). Defaults to today."
)
@click.option(
    "--desc",
    "--description",
    default=None,
    help="Custom description. Defaults to 'Opening balance - <account_name>'",
)
def set_cmd(account, amount, date, desc):
    """Set or update the starting balance for an accont."""
    set_opening_balance(account, amount, date, desc)
    click.echo(f"Saved opening balance for {account}")


@main.command(name="setup")
def setup():
    """Interative onboarding and account configuration wizard."""
    print_banner()
    print_system_diagnostic()
    if click.confirm("Wipe state: remove existing account data?", default=False):
        clear_bank_journals()
        clear_sync_state()
        click.echo("Cleared all account data (opening bank journals preserved).")

    run_setup()


@main.group(name="schedule")
def schedule():
    """Administer scheduled sync regime."""
    pass


@schedule.command(name="install")
@click.option(
    "--time", default="08:00", help="Sync time in 24-hr formation (e.g. 08:00)."
)
def schedule_install(time: str):
    """Install sync regime."""
    install_schedule(time_str=time)


@schedule.command(name="status")
def schedule_status():
    """Check active regime."""
    check_status()


@schedule.command(name="revoke")
def schedule_revoke():
    """Revoke active regime"""
    remove_schedule()
