"""Opening Balance Management module.

This scripts exposes functions that will help manage and review opening
balances.
"""

import re
from dataclasses import dataclass

from .paths import PATHS


@dataclass
class OpeningBalance:
    date: str
    account: str
    amount: float
    description: str


def get_balances() -> list[OpeningBalance]:
    journal_file = PATHS.data_dir / "accounts" / "opening_balances.journal"
    balances = []
    date = ""
    desc = ""
    account = ""
    amount = ""

    with open(journal_file, "r") as f:
        for line in f:
            if line.startswith(";") or not line.strip():
                continue

            if not line.startswith(" "):
                date, desc = line.strip().split(" * ", 1)

            else:
                if not line.strip().startswith("equity"):
                    account, raw = line.strip().split()
                    amount = float(re.sub(r"[^\d.-]", "", raw))
                    balances.append(
                        OpeningBalance(
                            date=date, account=account, amount=amount, description=desc
                        )
                    )
    return balances


if __name__ == "__main__":
    print(get_balances())
