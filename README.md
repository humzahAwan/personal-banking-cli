# `banking` — Terminal-First Plain-Text Accounting CLI

A terminal-native personal finance and cashflow analytics toolchain built in Python. `banking` connects UK Open Banking feeds (via [Lunchflow](https://lunchflow.app)) to [`hledger`](https://hledger.org/) double-entry accounting journals, providing automated background synchronization, regex-based transaction categorization, an interactive REPL shell, and in-terminal data visualisations powered by `plotext`.

---

## Key Features

- **Open Banking → Double-Entry Ledger Pipeline**: Fetches bank and credit card transactions via the Lunchflow API, deduplicates via persistent state tracking, and formats balanced `hledger` journal entries.
- **Regex Categorization Engine**: Automatically maps raw merchant descriptions to hierarchical double-entry accounts (`expenses:groceries`, `income:salary`, `assets:transfers:internal`, etc.) via customizable YAML rules.
- **XDG Base Directory Compliant**: Cleanly separates personal configuration (`~/.config/banking/`), API cache (`~/.cache/banking/`), and sync state (`~/.local/state/banking/`) from repository source code.
- **Automated Background Sync**: Native Linux `systemd --user` timer (`banking-sync.timer`) with `Persistent=true` for hands-off daily ledger updates.
- **Interactive Banking Shell (REPL)**: Dedicated terminal shell (`banking shell`) with live system diagnostics, account onboarding, and instant financial reporting shortcuts.
- **Terminal Visualisations & Cashflow Analytics**: Wraps `hledger` queries with `plotext` to render horizontal category spend bars, monthly cashflow comparisons, and balance trends directly inside the terminal.

---

## Architecture

```text
  Lunchflow Open Banking API
              │
              ▼
  ┌────────────────────────┐
  │   client.py (Session)  │──► ~/.cache/banking/ (JSON Cache)
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │     categorizer.py     │◄── ~/.config/banking/rules.yaml
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │  formatter.py / sync.py│──► ~/.local/state/banking/sync_state.json
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │   data/all.journal     │──► hledger + plotext (Terminal Visualisations)
  └────────────────────────┘
```

---

## Installation

### Prerequisites
- Python 3.11+
- [`hledger`](https://hledger.org/install.html) installed and available on `$PATH`
- A [Lunchflow](https://lunchflow.app) API key

### Setup

```bash
# Clone the repository
git clone git@github.com:humzahAwan/personal-banking-cli.git
cd personal-banking-cli

# Install in editable mode
pip install -e .

# Run the interactive onboarding wizard
banking setup
```

---

## Usage

### 1. Interactive Shell (`banking shell`)
Launch the interactive REPL environment with system telemetry and quick commands:

```bash
banking shell
```

Available shell commands:
| Command | Description |
| :--- | :--- |
| `setup` | Run interactive account discovery and onboarding wizard |
| `sync` | Synchronize transactions from bank feeds into journals |
| `schedule` | Check `systemd --user` background sync timer status |
| `bs` | Display Balance Sheet (Assets, Liabilities, Net Worth) |
| `balances` | Show liquid bank balances and credit card liabilities |
| `spend [--monthly] [depth]` | View expense breakdowns and cashflow analytics |
| `clear` | Clear terminal and reprint diagnostic banner |
| `help` | Display available shell commands |
| `exit` / `quit` | Close the banking shell |

### 2. Direct CLI Commands

```bash
# Sync transactions (use --refresh to bypass local cache)
banking sync --refresh

# Manage starting account balances
banking opening-balances list
banking opening-balances set assets:bank:savings 1000.00 --date 2024-09-01

# Configure daily background sync via systemd user timers
banking schedule install --time 08:00
banking schedule status
banking schedule revoke

# Reset journals/state (--cache for cache only, --hard for full wipe)
banking reset
```

---

## Project Structure

```text
banking/
├── pyproject.toml             # Package configuration & CLI entrypoint
├── rules.yaml                 # Default generic categorization rules template
├── data/                      # Local hledger journals (git-ignored)
│   ├── all.journal            # Master journal including all account ledgers
│   └── accounts/
│       ├── opening_balances.journal
│       ├── home.journal
│       ├── personal.journal
│       ├── savings.journal
│       └── amex.journal
└── src/banking/
    ├── cli.py                 # Click CLI command groups & entrypoint
    ├── shell.py               # Interactive REPL shell
    ├── banner.py              # CRT terminal banner & telemetry diagnostics
    ├── setup.py               # Account onboarding & config generator
    ├── client.py              # Lunchflow API client & local caching
    ├── categorizer.py         # Regex rule matching engine
    ├── formatter.py           # Double-entry hledger transaction formatter
    ├── sync.py                # Sync orchestrator & state deduplication
    ├── balances.py            # Opening balance parser & updater
    ├── reset.py               # Soft, cache, and hard reset utilities
    ├── scheduler.py           # systemd --user service & timer manager
    ├── reports.py             # hledger wrappers & plotext visualisations
    └── paths.py               # XDG Base Directory path resolution
```

---

## Roadmap & Progress

- [x] **Milestone 1 — Core Sync Pipeline**: Lunchflow API client, local caching, regex categorizer, double-entry `hledger` formatter, and stateful deduplication.
- [x] **Milestone 2 — CLI Core & Interactive Shell**: `banking setup`, `banking reset`, `banking opening-balances`, XDG path resolution, CRT diagnostic banner, and interactive REPL shell.
- [x] **Milestone 3 — Automated Scheduling**: Native `systemd --user` service and persistent daily timer integration (`install`, `status`, `revoke`).
- [ ] **Milestone 4 — Curated Reporting & Triage UX**:
  - [x] Core `hledger` wrappers (`bs`, `balances`, `spend`) wired into `banking shell`
  - [ ] Interactive unclassified transaction triage (`banking review`) to assign categories and update `~/.config/banking/rules.yaml`
  - [ ] Interactive transaction search & `$EDITOR` jump (`banking edit`)
- [ ] **Milestone 5 — Terminal Visualisations (`plotext`)**:
  - [ ] Horizontal bar charts for YTD and monthly category spend
  - [ ] Monthly income vs. expense cashflow trend charts in the terminal
  - [ ] Net worth & liquid balance trajectory plots
