"""
Data transformation module.

For any data transformations required to produce better analysis
"""

import csv
import io
import re
import subprocess

from .paths import PATHS


def _get_expenses_data(
    period: str = "this month", depth: int = 2, top_n: int = 10
) -> tuple[list[str], list[float]]:
    cmd = [
        "hledger",
        "-f",
        str(PATHS.master_journal),
        "balance",
        "expenses",
        "-p",
        period,
        "-S",
        "--depth",
        str(depth),
        "--no-total",
        "-O",
        "csv",
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    reader = csv.reader(io.StringIO(res.stdout))
    rows = list(reader)

    # if no data found in period.
    if len(rows) <= 1:
        return [], []

    categories = []
    amounts = []

    # header row is rows[0].
    for row in rows[1:]:
        raw_account = row[0]
        raw_amount = row[1]

        name = raw_account.replace("expenses:", "")
        val = float(re.sub(r"[^\d.-]", "", raw_amount))

        if val > 0:
            categories.append(name)
            amounts.append(val)

    if len(categories) > top_n:
        top_cats = categories[:top_n]
        top_amts = amounts[:top_n]
        other_amt = sum(amounts[top_n:])
        top_cats.append("other")
        top_amts.append(other_amt)
        return top_cats, top_amts

    return categories, amounts
