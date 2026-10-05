# Accountancy101 — Milestone 2

A small local accounting kernel for Cedar Desk Services. Approved assumptions:
USD, simplified accrual accounting, U.S. terminology, one checking account,
detailed early explanations. No tax or jurisdiction-specific reporting rules.

This milestone contains six accounts and five hand-written posted entries.
The fictional dates are January 1–5, 2026; all opening balances are zero.
It derives a ledger and trial balance and exports four readable CSV files.
It has no reconciliation, random data, learning UI, XLSX, AP/AR or later-stage features.

## Run locally (PowerShell)

From `C:\Users\Aaron\CoderVibe\Accountancy101`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[test]'
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m accountancy101
```

The environment and installation have already been prepared for this delivery.
Only the last two commands are needed to test and regenerate the sample outputs.
An optional `--output PATH` chooses another output folder. Re-running overwrites
the four sample CSV exports in the chosen folder.

## Files to read in order

1. `WALKTHROUGH.md`: accounting reasoning and independent manual checks.
2. `src/accountancy101/sample.py`: the six accounts and exact five entries.
3. `src/accountancy101/models.py`: immutable records and explicit debit/credit cents.
4. `src/accountancy101/accounting.py`: validation, posted ledger and trial balance.
5. `tests/test_accounting.py`: handwritten expected balances and failure cases.
6. `src/accountancy101/csv_output.py`: formatting and CSV export only.

`__main__.py` simply runs the fixed example. `pyproject.toml` defines the package
and pins the pytest test dependency; runtime uses only the standard library.
`tests/test_csv_output.py` checks exported values, quoting and exact formatting.
`ARCHITECTURE.md` retains the longer-term plan; implementation stops at Milestone 2.

## Inspect the output

| File in `outputs/milestone2/` | Contents |
|---|---|
| `accounts.csv` | Account IDs, names, types, normal sides |
| `journal.csv` | All ten journal lines, nested entry metadata flattened for reading |
| `ledger.csv` | Posted lines grouped by account, with each running balance |
| `trial_balance.csv` | Net ending balance per account and total row |

`*_minor` columns are authoritative integer cents. `*_usd` columns are readable
decimal dollar strings computed without floating-point arithmetic. CSV account
IDs are text by convention; Excel may infer their type when opening a CSV.
Ledger `running_net_debit_minor` is debits minus credits: negative means credit.
The readable running balance is an absolute magnitude with a separate side.
Trial-balance amounts use the actual ending side, not the account's normal side.
All chart accounts appear in the trial balance, including zero-balance accounts.

Draft entries are validated but do not affect the ledger or trial balance.
Duplicate account, entry or line identities are rejected rather than counted twice.
Inputs and outputs are immutable records in memory; these CSVs are exports, not
an ingestion workflow. No posting database or file-based correction workflow exists yet.

Expected Checking: **$4,925 debit**. Trial-balance totals: **$5,800 on each side**.
Total journal activity: **$6,675 on each side**; activity totals and net balance
totals answer different questions. Profit: **$125**. Equity after drawings: **$4,925**.
Balanced arithmetic does not prove the accounts or period were chosen correctly.
