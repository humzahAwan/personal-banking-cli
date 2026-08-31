import json
import os

import requests
from dotenv import load_dotenv

from .paths import PATHS

load_dotenv()


class Session:
    def __init__(self):

        self.API_KEY = os.environ.get("LUNCHFLOW_API_KEY")
        if self.API_KEY is None:
            raise ValueError(
                "LUNCHFLOW_API_KEY is missing"
                "Please define variable in .env or environment"
            )

        self.header = {"x-api-key": self.API_KEY, "Content-Type": "application/json"}
        self.base_url = "https://lunchflow.app/api/v1"
        self.transactions = {}

    def fetch_accounts(self, use_cache: bool = True) -> None:
        cache_file = PATHS.cache_dir / "accounts.json"

        if use_cache and cache_file.exists():
            with open(cache_file, "r") as f:
                self.accounts = json.load(f)
            return

        res = requests.get(f"{self.base_url}/accounts", headers=self.header, timeout=15)
        res.raise_for_status()
        self.accounts = res.json()

        with open(cache_file, "w") as f:
            json.dump(self.accounts, f, indent=2)

    def fetch_transactions(self, use_cache: bool = True) -> None:
        if not self.accounts:
            self.fetch_accounts()

        for acc in self.accounts.get("accounts", []):
            acc_id = acc["id"]
            cache_file = PATHS.cache_dir / f"{acc['id']}_transactions.json"

            if use_cache and cache_file.exists():
                with open(cache_file, "r") as f:
                    self.transactions[acc_id] = json.load(f)

            else:
                res = requests.get(
                    f"{self.base_url}/accounts/{acc_id}/transactions",
                    headers=self.header,
                    timeout=15,
                )
                res.raise_for_status()
                self.transactions[acc_id] = res.json()

                with open(cache_file, "w") as f:
                    json.dump(self.transactions[acc_id], f, indent=2)


if __name__ == "__main__":
    session = Session()
    session.fetch_accounts()
    print(f"Accounts: {len(session.accounts.get('accounts', []))}")
    session.fetch_transactions()
    print(f"Fetched transactions for accounts: {list(session.transactions.keys())}")
