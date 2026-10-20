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


def _get_accounts_list() -> list[str]:
    cmd = ["hledger", "-f", str(PATHS.master_journal), "accounts"]
    res = subprocess.run(cmd, capture_output=True, check=False, text=True)

    lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]

    return lines


def _build_account_tree(accounts: list[str]) -> dict:
    tree = {}

    for account in accounts:
        parts = account.split(":")
        current_node = tree

        for part in parts:
            current_node = current_node.setdefault(part, {})

    return tree


def _print_tree_node(
    node: dict, prefix: str = "", max_depth: int | None = None, current_depth: int = 1
) -> None:
    if max_depth is not None and current_depth > max_depth:
        return

    items = list(node.keys())

    for index, key in enumerate(items):
        is_last = index == len(items) - 1

        if is_last:
            connector = "└── "
            extension = "    "
        else:
            connector = "├── "
            extension = "│   "

        print(prefix + connector + key)

        next_prefix = prefix + extension
        child_dict = node[key]

        _print_tree_node(
            node=child_dict,
            prefix=next_prefix,
            max_depth=max_depth,
            current_depth=current_depth + 1,
        )


def report_accounts(tree: bool, depth: int | None = None) -> None:

    if tree:
        accounts = _get_accounts_list()
        tree_dict = _build_account_tree(accounts)
        _print_tree_node(tree_dict, max_depth=depth)

    else:
        args = ["accounts"]
        if depth is not None:
            args.extend(["--depth", str(depth)])
        _run_hledger(args)
