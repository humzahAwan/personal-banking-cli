"""
Transaction Formatter module.

Converts Lunchflow transaction dictionaries into double-entry plain-text
accounting format compliant with hledger.
"""

import logging
from typing import Any

import yaml

from .paths import PATHS

logger = logging.getLogger(__name__)

# Load configuration for default settings
if PATHS.config_file.is_file():
    with open(PATHS.config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
else:
    config = {}


def get_account_name(account_id: int, config: dict[str, Any]) -> str:
    """Look up the hledger account name for a Lunchflow account ID.

    Args:
        account_id: Numeric Lunchflow account identifier.
        config: Parsed configuration dictionary containing account mappings.

    Returns:
        The mapped hledger account name (e.g. 'assets:bank:home').
    """
    accounts = config.get("accounts", {})
    account_info = accounts.get(account_id) or accounts.get(str(account_id))
    if not account_info:
        logger.warning("Account ID %s not found in configuration", account_id)
        return f"assets:unknown:{account_id}"
    return account_info["name"]


def format_transaction(
    tx: dict[str, Any],
    account_name: str,
    category_name: str,
    currency_symbol: str = "£",
) -> str:
    """Format a raw Lunchflow transaction dictionary into an hledger entry string.

    Args:
        tx: Transaction record containing date, merchant, amount, etc.
        account_name: Target bank or liability account name.
        category_name: Target expense or income category account name.
        currency_symbol: Currency symbol prefix (default '£').

    Returns:
        A multi-line hledger journal entry string ending with a newline.
    """
    entry = []
    indent = " " * 4

    # 1. Header Line: Date, Status Flag, Payee / Description
    date = tx.get("date", "1970-01-01")
    flag = "!" if tx.get("isPending") else "*"
    merchant = tx.get("merchant") or tx.get("description") or "Unknown Payee"
    entry.append(f"{date} {flag} {merchant}")

    # 2. Metadata Comment: Lunchflow Unique ID
    tx_id = tx.get("id", "unknown")
    entry.append(f"{indent}; lunchflow_id: {tx_id}")

    # 3. Postings (Double-Entry Legs)
    amount = float(tx.get("amount", 0.0))

    # Category posting (opposite sign of bank amount)
    category_amt = (
        f"{currency_symbol}{abs(amount):.2f}"
        if amount < 0
        else f"-{currency_symbol}{amount:.2f}"
    )
    entry.append(f"{indent}{category_name:<45} {category_amt:>10}")

    # Bank posting (retains original transaction sign)
    bank_amt = (
        f"-{currency_symbol}{abs(amount):.2f}"
        if amount < 0
        else f"{currency_symbol}{amount:.2f}"
    )
    entry.append(f"{indent}{account_name:<45} {bank_amt:>10}")

    logger.debug(
        "Formatted transaction %s (%s): %s -> %s",
        tx_id,
        date,
        account_name,
        category_name,
    )

    return "\n".join(entry) + "\n"


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    sample_tx = {
        "id": "16ea18aaec66ccd35dd77e79b527b063",
        "accountId": 34698,
        "amount": -21.95,
        "currency": "GBP",
        "date": "2026-08-28",
        "merchant": "TESCO STORES 2141 BRISLINGTON",
        "description": "TESCO STORES 2141 BRISLINGTON",
        "isPending": False,
    }

    bank = get_account_name(sample_tx["accountId"], config)
    defaults = config.get("defaults", {})
    category = defaults.get("expense_account", "expenses:unclassified")

    formatted = format_transaction(sample_tx, account_name=bank, category_name=category)
    print("\n--- Output Test ---")
    print(formatted)
