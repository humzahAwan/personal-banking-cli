"""
These functions will wrap hledger processes to create clean functions for the banking API
"""

import subprocess

from .paths import PATHS


def _run_hledger(args: list[str]) -> None:
    """Helper to execute hledger against the master journal."""
    cmd = ["hledger", "-f", str(PATHS.master_journal)] + args
    subprocess.run(cmd, check=False)


def report_bs() -> None:
    """Balance Sheet: Assests, Liabilities and Net Worth"""
    _run_hledger(["bs"])


def report_spend(monthly: bool = False, depth: int = 2) -> None:
    """Expense summary of monthly income/expense cashflow."""
    if monthly:
        # Income statement grouped by month for the current year.
        _run_hledger(["is", "--monthly", "-p", "this year"])
    else:
        # Total expense grouped up to "depth"
        _run_hledger(["balance", "expenses", "--depth", str(depth)])
