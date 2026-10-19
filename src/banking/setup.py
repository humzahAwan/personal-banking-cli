"""
This module exposes logic consumed by the cli banking setup wizard.
"""

import os

import click
import yaml
from dotenv import load_dotenv, set_key

from .client import Session
from .paths import PATHS
from .reset import clear_bank_journals, clear_sync_state
from .sync import run_sync

load_dotenv()


def save_api_key(api_key: str) -> None:
    """Save new api_key to .env file.

    Args:
        api_key: Lunchflow api key.
    """

    env_file = PATHS.project_root / ".env"
    set_key(env_file, "LUNCHFLOW_API_KEY", api_key)
    os.environ["LUNCHFLOW_API_KEY"] = api_key


def ensure_api_key():
    api_key = os.environ.get("LUNCHFLOW_API_KEY")
    if not api_key:
        api_key = click.prompt("Enter API Key", hide_input=True)
        save_api_key(api_key)


def configure_accounts(account_list) -> None:
    # initialise config dictionary.
    config = {
        "accounts": {},
        "defaults": {
            "currency_symbol": "£",
            "expense_account": "expenses:unclassified",
            "income_account": "income:unclassified",
        },
    }
    click.echo(f"\nFound {len(account_list)} accounts:")
    for acc in account_list:
        acc_id = acc["id"]
        acc_name = acc["name"]

        click.echo(f"\nFound bank account: {acc_name} (ID: {acc_id})")
        hledger_name = click.prompt(
            " hledger account name", default=f"assets:bank:{acc_name}"
        )
        journal_file = hledger_name.split(":")[-1]
        journal_path = click.prompt(
            " journal_path", default=f"data/accounts/{journal_file}.journal"
        )

        # save into config dictionary.
        config["accounts"][acc_id] = {
            "name": hledger_name,
            "journal": journal_path,
            "currency": "GBP",
        }

    # write config dictionary to config.yaml
    with open(PATHS.config_file, "w") as f:
        yaml.safe_dump(config, f)

    click.echo("\n Saved config.yaml successfully!")


def run_setup():
    if click.confirm("Wipe state: remove existing account data?", default=False):
        clear_bank_journals()
        clear_sync_state()
        click.echo("Cleared all account data (opening bank journals preserved).")

    ensure_api_key()
    session = Session()
    session.fetch_accounts(use_cache=False)
    account_list = session.accounts.get("accounts", [])

    configure_accounts(account_list)

    if click.confirm("Run initial sync now?", default=True):
        run_sync(use_cache=False)
        click.echo("Initial sync complete!")
