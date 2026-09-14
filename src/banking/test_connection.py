import json
import os
import sys

import requests
from dotenv import load_dotenv


def test_response() -> None:
    load_dotenv()

    API_KEY = os.getenv("LUNCHFLOW_API_KEY")

    if not API_KEY:
        print(
            "Configuration Error: 'LUNCHFLOW_API_KEY' is missing in .env",
            file=sys.stderr,
        )
        print(
            "Please create a .env file with: LUNCHFLOW_API_KEY=my_key", file=sys.stderr
        )
        sys.exit(1)

    header = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    base_url = "https://lunchflow.app/api/v1"

    # Fetch accounts information.
    print("Fetching accounts...")
    res_accounts = requests.get(f"{base_url}/accounts", headers=header)

    if res_accounts.status_code == 200:
        accounts = res_accounts.json()
        print("Accounts retrieved:")
        print(json.dumps(accounts, indent=2))
    else:
        print(
            f"Failed to fetch accounts (HTTP {res_accounts.status_code})",
            file=sys.stderr,
        )
        print(res_accounts.text, file=sys.stderr)
        sys.exit(1)

    # Fetch transactions.
    for acc in accounts.get("accounts", []):
        acc_id = acc["id"]
        acc_name = acc["name"]
        insta_name = acc["institution_name"]

        print(f"Fetching transactions for : {insta_name} (ID: {acc_id})...")
        res_tx = requests.get(
            f"{base_url}/accounts/{acc_id}/transactions", headers=header
        )

        if res_tx.status_code == 200:
            tx_data = res_tx.json()
            tx_list = tx_data.get("transactions", [])
            print(f"Retrieved {len(tx_list)} transactions. From {acc_name}")
            if tx_list:
                print("Sample transaction:")
                print(json.dumps(tx_list[0], indent=4))

        else:
            print(f"HTTP {res_tx.status_code}: {res_tx.text}", file=sys.stderr)
            print("-" * 60)


if __name__ == "__main__":
    test_response()
