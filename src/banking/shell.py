"""
Banking shell module.

Interactive Terminal Shell (REPL) for the Banking CLI.
"""

import click

from .banner import print_banner, print_system_diagnostic
from .reports import report_accounts, report_bs, report_spend
from .scheduler import check_status
from .setup import run_setup
from .sync import run_sync


def print_help_menu() -> None:
    """Displays available commands in the interactive shell."""
    click.echo("\n  COMMAND           DESCRIPTION")
    click.echo("  " + "─" * 45)
    click.echo("  setup             Run account onboarding wizard")
    click.echo("  sync              Synchronize transactions from bank feeds")
    click.echo("  schedule          Check background sync timer status")
    click.echo("  balances          Check liquid balances and credit card liabilty")
    click.echo("  spend             Time series spend analystics")
    click.echo("  accounts          Return all hlsdger accounts")
    click.echo("  clear             Clear screen and reprint banner")
    click.echo("  help              Display this command menu")
    click.echo("  exit / quit       Exit the banking shell\n")


def read_depth(args):
    for arg in args:
        if arg.isdigit():
            return int(arg)


def run_interactive_shell() -> None:
    """Launches the interactive banking shell session."""
    click.clear()
    print_banner()
    print_system_diagnostic()

    while True:
        try:
            raw_input = click.prompt("banking", prompt_suffix=": ").strip().lower()
            if not raw_input:
                continue

            raw_input = raw_input.split()
            cmd = raw_input[0]
            args = raw_input[1:]

            if cmd in ("exit", "quit", "q"):
                click.echo("Session closed. Goodbye!")
                break

            elif cmd in ("help", "?"):
                print_help_menu()

            elif cmd == "setup":
                run_setup()

            elif cmd == "sync":
                click.echo("Running sync...")
                run_sync()
                click.echo("✓ Sync completed!")

            elif cmd == "schedule":
                check_status()

            elif cmd == "balances":
                click.echo("Reading balances...")
                report_bs()

            elif cmd == "spend":
                click.echo("Writing spend report...")
                is_monthly = "--monthly" in args
                depth = read_depth(args)

                report_spend(monthly=is_monthly)

            elif cmd == "accounts":
                click.echo("Collecting all hledger accounts")
                is_tree = "--tree" in args
                depth = read_depth(args)

                report_accounts(tree=is_tree, depth=depth)

            elif cmd in ("clear", "banner"):
                click.clear()
                print_banner()
                print_system_diagnostic()

            else:
                click.secho(
                    f"Unknown command: '{cmd}'. Type 'help' for available commands.",
                    fg="yellow",
                )

        except (KeyboardInterrupt, EOFError):
            click.echo("\nSession closed.")
            break
