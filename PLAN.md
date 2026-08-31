# Lunchflow to hledger Integration Plan

This document outlines the step-by-step implementation plan for syncing transactions from the Lunchflow API into `hledger` plain-text accounting journals.

---

## 1. Overview & Discovered Accounts

Detected active accounts from Lunchflow:
- **American Express** (`ID: 34699`): British Airways American Express®
- **First Direct** (`ID: 34698`): 1st Account (Primary)
- **First Direct** (`ID: 34697`): 1st Account (Secondary)
- **First Direct** (`ID: 34696`): Savings Account

---

## 2. Directory Layout & XDG Standards

### Project Repository (`~/banking`)
```text
banking/
├── .env                       # API secret (git-ignored)
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore rules
├── config.yaml                # Account mapping & sync options
├── rules.yaml                 # Categorization regex rules
├── PLAN.md                    # This plan document
├── data/
│   ├── all.journal            # Master journal including all account journals
│   └── accounts/
│       ├── amex_ba.journal
│       ├── fd_current_1.journal
│       ├── fd_current_2.journal
│       └── fd_savings.journal
└── src/
    ├── test_connection.py
    ├── client.py              # Lunchflow API client
    ├── sync.py                # Main sync orchestrator & CLI
    └── categorizer.py         # Payee rule matching & transaction formatting
```

### Linux XDG Standard Paths
- **API Cache**: `~/.cache/banking/` (Disposable raw API JSON payloads)
- **Sync State**: `~/.local/state/banking/` (`sync_state.json` tracking last sync timestamp and imported transaction IDs)

---

## 3. Step-by-Step Implementation Plan

### Step 1: Repository Hygiene & Security
1. Create `.gitignore` to ignore:
   - Secrets: `.env`, `.env.*`, `!.env.example`
   - Python artifacts: `__pycache__/`, `*.py[cod]`, `.venv/`
2. Create `.env.example` documenting `LUNCHFLOW_API_KEY=your_key_here`.

### Step 2: Account Mapping & Configuration
1. Create `config.yaml` to define:
   - Lunchflow account ID to hledger account hierarchy mappings:
     - `34699` -> `liabilities:credit:amex:ba`
     - `34698` -> `assets:bank:firstdirect:current1`
     - `34697` -> `assets:bank:firstdirect:current2`
     - `34696` -> `assets:bank:firstdirect:savings`
   - Default offset accounts (`expenses:unclassified`, `income:unclassified`).
   - Currency formatting (`£` / `GBP`).

### Step 3: XDG State & Cache Management
1. Implement path resolution using `$XDG_CACHE_HOME` (`~/.cache/banking`) and `$XDG_STATE_HOME` (`~/.local/state/banking`).
2. Define the `sync_state.json` schema to track:
   - `last_sync_timestamp` per account.
   - Set of already imported transaction UUIDs to guarantee idempotency and prevent duplicates.

### Step 4: Data Ingestion & Sync Pipeline
1. Build `src/client.py` for interacting with the Lunchflow API (`/accounts`, `/accounts/{id}/transactions`).
2. Add caching logic to write and read raw responses to/from `~/.cache/banking/` (enabling offline rule tweaking and rate-limit preservation).
3. Implement incremental querying to only request transactions created or updated since the last sync.

### Step 5: Plain Text Accounting (PTA) Transformation
1. Format JSON records into standard `hledger` syntax:
   - **Date**: `YYYY-MM-DD`
   - **Status flag**: `*` (cleared, `isPending: false`) or `!` (pending, `isPending: true`)
   - **Payee & Description**: Extracted from `merchant` and `description`
   - **Metadata tags**: Attached as comments (`; lunchflow_id: <uuid>`)
   - **Postings**: Two-legged double-entry posting balancing the bank account and expense/income account.

### Step 6: Rule-Based Categorization Engine
1. Build `rules.yaml` with regex rules matching merchant/description patterns to expense/income accounts (e.g. supermarkets -> `expenses:groceries`, interest -> `income:interest`).
2. Fallback unmatched transactions to `expenses:unclassified` so the journal remains balanced.

### Step 7: Master Journal Structure
1. Separate journals by account under `data/accounts/`.
2. Configure `data/all.journal` using `include accounts/*.journal` to provide a unified financial ledger.

### Step 8: CLI Interface & Validation
1. Build `src/sync.py` CLI supporting flags like `--dry-run`, `--refresh-cache`, and `--account-id`.
2. Validate entries using `hledger -f data/all.journal check`.

### Step 9: Automation (Optional)
1. Set up a daily cron job or systemd user timer to run the sync script automatically.
