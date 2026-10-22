"""
Sync Scheduler.

Scheduler module for creating sync schedules.
"""

import shutil
import subprocess
from os import sync
from pathlib import Path

import click

SYSTEMD_USER_DIR = Path.home() / ".config" / "systemd" / "user"
SERVICE_FILE = SYSTEMD_USER_DIR / "banking-sync.service"
TIMER_FILE = SYSTEMD_USER_DIR / "banking-sync.timer"


def install_schedule(time_str: str = "08:00") -> None:
    """Creates daily systemd user timer"""

    SYSTEMD_USER_DIR.mkdir(parents=True, exist_ok=True)

    banking_bin = shutil.which("banking")
    if not banking_bin:
        raise RuntimeError("Could not find 'banking' command in PATH")

    service_content = f"""[Unit]
    Description=Daily Lunchflow Banking Ledger sync

    [Service]
    Type=oneshot
    ExecStart={banking_bin} sync
    """
    with open(SERVICE_FILE, "w") as f:
        f.write(service_content)

    timer_content = f"""[Unit]
    Description=Run daily banking sync at {time_str}

    [Timer]
    OnCalendar=*-*-* {time_str}:00
    Persistent=True

    [Install]
    WantedBy=timers.target
    """
    with open(TIMER_FILE, "w") as f:
        f.write(timer_content)

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(
        ["systemctl", "--user", "enable", "--now", "banking-sync.timer"],
        capture_output=True,
        check=True,
    )
    click.echo(f"Daily sync scheduled at {time_str} everyday!")


def check_status() -> None:
    """Checkes whether the systemd timer is active"""

    if not TIMER_FILE.exists():
        click.echo("Schedule status: NOT INSTALLED")
        return

    result = subprocess.run(
        ["systemctl", "--user", "is-active", "banking-sync.timer"],
        capture_output=True,
        text=True,
        check=False,
    )
    status = result.stdout.strip()
    click.echo(f"Schedule status: {status.upper()}")

    subprocess.run(
        ["systemctl", "--user", "list-timers", "banking-sync.timer"], check=False
    )


def remove_schedule() -> None:
    """Stops and deletes systemd user timer and service"""

    if not TIMER_FILE.exists() and not SERVICE_FILE.exists():
        click.echo("No scheduled sync found to remove.")
        return

    # Stop and disable the timer
    subprocess.run(
        ["systemctl", "--user", "disable", "--now", "banking-sync.timer"],
        capture_output=True,
        check=False,
    )

    # Delete the configuration files
    SERVICE_FILE.unlink(missing_ok=True)
    TIMER_FILE.unlink(missing_ok=True)

    # Reload systemd
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    click.echo("Scheduled daily sync has been removed.")
