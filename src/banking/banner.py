"""
These functions are used to create the setup wizard banner.
"""

import os
import shutil
import sys
import time

import click

from .paths import PATHS

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
    click.clear()
    """Creates a CRT-style cyberpunk scanline animation."""
    for line in BANNER.splitlines():
        # Telemetry/status lines get high-tech cyan color with typewriter rhythm:
        if "FINANCIAL PROTOCOL" in line or "NET://" in line or "PERSON" in line:
            for char in line:
                click.secho(char, fg="cyan", bold=True, nl=False)
                sys.stdout.flush()
                delay = 0.0002 if char == " " else 0.004
                time.sleep(delay)
            click.echo()
            time.sleep(0.03)
        else:
            # Main logo & borders draw in phosphor green with fast-forwarded whitespace:
            for char in line:
                click.secho(char, fg="green", bold=True, nl=False)
                sys.stdout.flush()
                delay = 0.0002 if char == " " else 0.0018
                time.sleep(delay)
            click.echo()
            time.sleep(0.02)


def print_system_diagnostic():
    click.secho("\n  [ SYSTEM TELEMETRY ]", fg="bright_black", bold=True)
    click.echo("  " + "─" * 45)

    # python & conda environment.
    conda_env = os.environ.get("CONDA_DEFAULT_ENV", "system")
    py_ver = f"{sys.version.split()[0]} (env: {conda_env})"
    click.secho(f"  • {'Python Runtime':<18} : {py_ver}", fg="cyan")

    # Check hledger installation.
    hledger_path = shutil.which("hledger")
    hledger_status = (
        "INSTALLED" if hledger_path else "NOT FOUND (Required for report engine!)"
    )
    click.secho(f"  • {'hledger Binary':<18} : {hledger_status}", fg="cyan")

    # Check existing config files.
    has_env = (PATHS.project_root / ".env").exists()
    has_config = PATHS.config_file.exists()
    click.secho(
        f"  • {'API Key (.env)':<18} : {'FOUND' if has_env else 'NOT CONFIGURED'}",
        fg="cyan",
    )
    click.secho(
        f"  • {'Config File':<18} : {'FOUND' if has_config else 'NOT FOUND (Creating..)'}",
        fg="cyan",
    )

    # Count existing journals
    accounts_dir = PATHS.data_dir / "accounts"
    bank_journals = [
        f
        for f in accounts_dir.glob("*.journal")
        if f.name != "opening_balances.journal"
    ]
    has_opening = (accounts_dir / "opening_balances.journal").exists()
    click.secho(
        f"  • {'Bank Feeds':<18} : {len(bank_journals)} active journals",
        fg="cyan",
    )
    click.secho(
        f"  • {'Opening Balances':<18} : {'FOUND' if has_opening else 'NOT CONFIGURED'}",
        fg="cyan",
    )
    click.echo("  " + "─" * 45 + "\n")


if __name__ == "__main__":
    print_banner()
    print_system_diagnostic()
