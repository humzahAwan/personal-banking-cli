"""Opening Balance Management module.

This scripts exposes functions that will help manage and review opening
balances.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from .paths import PATHS


@dataclass
class OpeningBalance:
    date: str
    account: str
    amount: float
    description: str


def get_balances() -> list[OpeningBalance]:
    """Parse opening balances from opening_balances.journal"""
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


def set_opening_balance(
    account: str, amount: float, date: str | None = None, desc: str | None = None
) -> None:
    balances = get_balances()
    found = False

    for b in balances:
        if b.account == account:
            b.amount = amount

            if date is not None:
                b.date = date
            if desc is not None:
                b.description = desc

            found = True

    if not found:
        if not date:
            date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        if not desc:
            desc = f"Opening Balance - {account.split(':')[-1].capitalize()}"

        balances.append(
            OpeningBalance(date=date, account=account, amount=amount, description=desc)
        )

    file = PATHS.opening_balances

    with open(file, "w") as f:
        f.write("; OPENING/n/n")

        for b in balances:
            if b.amount == 0:
                continue
            if b.amount >= 0:
                account_str = f"£{b.amount:.2f}"
                equity_str = f"-£{b.amount:.2f}"
            else:
                account_str = f"-£{abs(b.amount):.2f}"
                equity_str = f"£{abs(b.amount):.2f}"

            entry = (
                f"\n{date} * Opening Balance - {b.account}\n"
                f"    {b.account:<42} {account_str:>10}\n"
                f"    {'equity:opening-balances':<42} {equity_str:>10}\n"
            )

            f.write(entry)


if __name__ == "__main__":
    print(get_balances())
