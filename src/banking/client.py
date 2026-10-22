"""
Lunchflow API Client module.

Handles authentication, fetching accounts, fetching transactions,
and local disk caching.
"""

import json
import logging
import os
from typing import Any

import requests
import yaml
from dotenv import load_dotenv

from .paths import PATHS

load_dotenv()

logger = logging.getLogger(__name__)


class Session:
    """Client session for interacting with the Lunchflow API."""

    def __init__(self) -> None:
        """Initialize session with API credentials and configuration."""
        self.api_key: str | None = os.environ.get("LUNCHFLOW_API_KEY")
        if not self.api_key:
            raise ValueError(
                "LUNCHFLOW_API_KEY is missing. "
                "Please define it in your .env file or environment."
            )

        self.header: dict[str, str] = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        self.base_url: str = "https://lunchflow.app/api/v1"
        self.accounts: dict[str, Any] = {}
        self.transactions: dict[int, Any] = {}

    def fetch_accounts(self, use_cache: bool = True) -> None:
        """Fetch all user accounts from the Lunchflow API or local cache.

        Args:
            use_cache: If True, load from cache if available on disk.
        """
        cache_file = PATHS.cache_dir / "accounts.json"

        if use_cache and cache_file.exists():
            logger.info("Loading accounts from cache: %s", cache_file)
            with open(cache_file, "r") as f:
                self.accounts = json.load(f)
            return

        logger.info("Fetching accounts from live API...")
        res = requests.get(f"{self.base_url}/accounts", headers=self.header, timeout=15)
        res.raise_for_status()
        self.accounts = res.json()

        logger.debug("Writing accounts to cache: %s", cache_file)
        with open(cache_file, "w") as f:
            json.dump(self.accounts, f, indent=2)

    def fetch_transactions(
        self, acc_id: int, acc_name: str, use_cache: bool = True
    ) -> None:
        """Fetch transactions for all accounts from the API or local cache.

        Args:
            use_cache: If True, load from cache if available on disk.
        """
        cache_file = PATHS.cache_dir / f"{acc_id}_transactions.json"

        if use_cache and cache_file.exists():
            logger.info(
                "Loading transactions for '%s' (ID: %s) from cache",
                acc_name,
                acc_id,
            )
            with open(cache_file, "r") as f:
                self.transactions[acc_id] = json.load(f)
        else:
            logger.info(
                "Fetching live transactions for '%s' (ID: %s)...",
                acc_name,
                acc_id,
            )
            res = requests.get(
                f"{self.base_url}/accounts/{acc_id}/transactions",
                headers=self.header,
                timeout=15,
            )
            res.raise_for_status()
            self.transactions[acc_id] = res.json()

            logger.debug("Writing transactions to cache: %s", cache_file)
            with open(cache_file, "w") as f:
                json.dump(self.transactions[acc_id], f, indent=2)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    session = Session()
    session.fetch_accounts()
    print(f"Accounts loaded: {len(session.accounts.get('accounts', {}))}")

    file = PATHS.config_file
    with open(file, "r") as f:
        config = yaml.safe_load(f)

    for acc_id in config.get("accounts"):
        acc_name = config["accounts"][acc_id].get("name")
        session.fetch_transactions(acc_id, acc_name)

    print(f"Fetched transactions for accounts: {list(session.transactions.keys())}")
