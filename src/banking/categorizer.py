"""Transaction Categorizer module.

Matches transaction payees and descriptions against rules defined in rules.yaml
to determine double-entry expense and income accounts.
"""

import logging
import re
from typing import Any

import yaml

from .paths import PATHS

logger = logging.getLogger(__name__)


class Categorizer:
    """Categorizes transactions into hledger accounts using regex patterns."""

    def __init__(self, rules: list[dict[str, str]] | None = None) -> None:
        """Initialize categorizer with rules or load from PATHS.rules_file."""
        if rules is not None:
            raw_rules = rules
        elif PATHS.rules_file.is_file():
            with open(PATHS.rules_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                raw_rules = data.get("rules", [])
        else:
            logger.warning("No rules.yaml found at %s", PATHS.rules_file)
            raw_rules = []

        # Precompile regex patterns for performance
        self.compiled_rules: list[tuple[re.Pattern, str]] = []
        for r in raw_rules:
            try:
                pattern = re.compile(r["pattern"])
                self.compiled_rules.append((pattern, r["account"]))
            except re.error as e:
                logger.error("Invalid regex in rule '%s': %s", r.get("pattern"), e)

    def categorize(self, tx: dict[str, Any], defaults: dict[Any, str] | None) -> str:
        """Categorize a transaction based on merchant/description or fallback.

        Args:
            tx: Transaction dictionary from Lunchflow.
            defaults: Fallback defaults dictionary from config.yaml.

        Returns:
            The matched or fallback hledger account name.
        """
        if not defaults:
            raise ValueError(
                "Default accounts missing from config."
                "Please add default expense and income accounts to config."
            )

        merchant = tx.get("merchant") or ""
        description = tx.get("description") or ""
        text = f"{merchant} {description}".strip()

        for pattern, account in self.compiled_rules:
            if pattern.search(text):
                return account

        # Fallback based on amount sign
        amount = tx.get("amount", 0.0)
        if amount < 0:
            return defaults.get("expense_account", "expenses:unclassified")
        return defaults.get("income_account", "income:unclassified")


if __name__ == "__main__":
    categorizer = Categorizer()
    print(f"Loaded {len(categorizer.compiled_rules)} rules.")

    defaults = {
        "expense_account": "expenses:unclassified",
        "income_account": "income:unclassified",
    }

    sample_tx = {
        "merchant": "TESCO STORES 2141 BRISLINGTON",
        "description": "TESCO STORES 2141 BRISLINGTON",
        "amount": -21.95,
    }
    print("Sample category:", categorizer.categorize(sample_tx, defaults))
