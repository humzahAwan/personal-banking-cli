"""
This module is called as part of the process for resetting the accounting system.

In the case that a reset was needed to fix some error. These function provide
clean directories before resync.
"""

from .paths import PATHS


def clear_sync_state() -> None:
    """Deletes the state file containing IDs for all synced transactions"""
    PATHS.sync_state_file.unlink(missing_ok=True)


def clear_bank_journals() -> None:
    """Deletes the all journals data/accounts/<account_name>.journal not
    opening_balances.journal
    """
    accounts_dir = PATHS.data_dir / "accounts"

    for file in accounts_dir.glob("*.journal"):
        if file.name != "opening_balances.journal":
            file.unlink()


def clear_cache():
    """Clear all files from cache"""
    for file in PATHS.cache_dir.iterdir():
        file.unlink()
