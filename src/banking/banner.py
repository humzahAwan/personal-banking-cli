"""
These functions are used to create the setup wizard banner.
"""

import sys
import time

import click

BANNER = r"""
     ┌─────────────────────────────────────────────────────────────┐
     │  ██████╗  █████╗ ███╗   ██╗██╗  ██╗██╗███╗   ██╗ ██████╗    │
     │  ██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝██║████╗  ██║██╔════╝    │
     │  ██████╔╝███████║██╔██╗ ██║█████═╝ ██║██╔██╗ ██║██║  ███╗   │
     │  ██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ ██║██║╚██╗██║██║   ██║   │
     │  ██████╔╝██║  ██║██║ ╚████║██║ ╚██╗██║██║ ╚████║╚██████╔╝   │
     │  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝    │
     ├─────────────────────────────────────────────────────────────┤
     │  [PERSON FINANCIAL PROTOCOL] // ACCOUNT ONBOARDING & SETUP  │
     │  NET://LUNCHFLOW.SYNC // SECURE_SETUP: TRUE                 │
     └─────────────────────────────────────────────────────────────┘
    """


def print_banner():
    """Creates crt style animation that prints the global BANNER variable"""

    for line in BANNER.splitlines():
        for char in line:
            click.secho(char, fg="green", bold=True, nl=False)
            sys.stdout.flush()
            time.sleep(0.005)  # 5 ms per char

        click.echo()
        time.sleep(0.04)  # 40 mseconds delay between line
