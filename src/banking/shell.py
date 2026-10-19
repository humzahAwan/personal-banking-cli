"""Interactive Terminal Shell (REPL) for the Banking CLI."""

import click

from .banner import print_banner, print_system_diagnostic
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
    click.echo("  clear             Clear screen and reprint banner")
    click.echo("  help              Display this command menu")
    click.echo("  exit / quit       Exit the banking shell\n")


def run_interactive_shell() -> None:
    """Launches the interactive banking shell session."""
    click.clear()
    print_banner()
    print_system_diagnostic()

    while True:
        try:
            cmd = click.prompt("banking", prompt_suffix=": ").strip().lower()

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

            elif cmd in ("clear", "banner"):
                click.clear()
                print_banner()
                print_system_diagnostic()

            elif cmd == "":
                continue

            else:
                click.secho(
                    f"Unknown command: '{cmd}'. Type 'help' for available commands.",
                    fg="yellow",
                )

        except (KeyboardInterrupt, EOFError):
            click.echo("\nSession closed.")
            break
