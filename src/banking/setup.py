"""
This module exposes logic consumed by the cli banking setup wizard.
"""

import os

import click
from dotenv import load_dotenv, set_key

from .client import Session
from .paths import PATHS

dotenv.load_dotenv


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


def run_setup():
    ensure_api_key()
    session = Session()
    session.fetch_accounts(use_cache=False)
