"""
Plotter module.

These functions draw visualisations to the terminal.
"""

import plotext as plt

from .transforms import _get_expenses_data


def plot_expenses(period: str = "this month", depth: int = 2) -> None:
    cats, amts = _get_expenses_data(period=period, depth=depth)

    if not cats:
        print(f"No expenses recorded in period: {period}")
        return

    # plotext horizontal bar chart
    cats.reverse()
    amts.reverse()

    width, _ = plt.terminal_size()
    height = len(cats) * 2 + 3

    plt.clf()
    plt.theme("clear")
    plt.plotsize(width, height)

    plt.bar(cats, amts, orientation="horizontal", width=0.1)
    plt.title(f"Expenses ({period})")
    plt.show()
