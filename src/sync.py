"""Sync Orchestrator module.

Coordinates fetching transactions, deduplicating with sync_state.json,
categorizing, and appending to hledger plain-text accounting journals.
"""

import json
from pathlib import Path
from typing import Any

import yaml

from .categorizer import Categorizer
from .client import Session
from .formatter import format_transaction
from .paths import PATHS


def load_config() -> dict[str, Any]:
    with open(PATHS.config_file, "r") as f:
        return yaml.safe_load(f)


def load_state() -> dict[str, list[str]]:
    file = PATHS.sync_state_file
    if PATHS.sync_state_file.exists():
        with open(file, "r") as f:
            return json.load(f)
    else:
        return {}


def save_state(state: dict[str, list[str]]) -> None:
    PATHS.sync_state_file.parent.mkdir(parents=True, exist_ok=True)
    file = PATHS.sync_state_file
    with open(file, "w") as f:
        json.dump(state, f)


def ensure_master_journal(master_path: Path = Path("data/all.journal")) -> None:
    master_path.parent.mkdir(parents=True, exist_ok=True)

    if not master_path.exists():
        with open(master_path, "w", encoding="utf-8") as f:
            f.write("; Master Journal - combines all account ledgers\n")
            f.write("include accounts/*.journal\n")


def run_sync(use_cache: bool = True) -> None:
    session, categorizer, state = Session(), Categorizer(), load_state()
    config = load_config()
    ensure_master_journal()

    for acc_id, acc_info in config.get("accounts", {}).items():
        acc_id = int(acc_id)
        acc_name = acc_info["name"]
        journal_file = Path(acc_info["journal"])

        session.fetch_transactions(acc_id, acc_name, use_cache=use_cache)

        synced_ids = set(state.get(str(acc_id), []))

        transactions = session.transactions[acc_id].get("transactions", [])

        new_txs = [
            tx
            for tx in transactions
            if not tx["isPending"] and tx.get("id") not in synced_ids
        ]

        entries = [
            format_transaction(
                tx, acc_name, categorizer.categorize(tx, config.get("defaults"))
            )
            for tx in new_txs
        ]

        journal_file.parent.mkdir(parents=True, exist_ok=True)
        with open(journal_file, "a") as f:
            f.writelines(entries)

        synced_ids.update(tx["id"] for tx in new_txs)

        state[str(acc_id)] = list(synced_ids)

    save_state(state)


if __name__ == "__main__":
    run_sync(use_cache=True)
