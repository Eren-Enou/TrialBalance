"""Readable CSV exports only; ingestion and XLSX belong to Milestone 3."""

import csv
from pathlib import Path

from .accounting import derive_ledger, derive_trial_balance
from .models import Account, JournalEntry


def dollars(cents: int) -> str:
    """Exact display formatting without floating-point money arithmetic."""
    sign = "-" if cents < 0 else ""
    whole, fraction = divmod(abs(cents), 100)
    return f"{sign}{whole}.{fraction:02d}"


def _write(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def export_csv(
    output_dir: Path, accounts: tuple[Account, ...], entries: tuple[JournalEntry, ...]
) -> None:
    """Validate before writing; overwrite these four derived sample exports."""
    ledger = derive_ledger(accounts, entries)
    trial = derive_trial_balance(accounts, entries)
    names = {account.account_id: account.name for account in accounts}
    output_dir.mkdir(parents=True, exist_ok=True)
    _write(output_dir / "accounts.csv", (
        "account_id", "name", "account_type", "normal_side",
    ), [dict(account_id=a.account_id, name=a.name,
             account_type=a.account_type.value, normal_side=a.normal_side.value)
        for a in sorted(accounts, key=lambda a: a.account_id)])

    journal_rows = []
    for entry in sorted(entries, key=lambda e: (e.posting_date, e.entry_id)):
        for line in sorted(entry.lines, key=lambda line: line.line_number):
            journal_rows.append(dict(
                entry_id=entry.entry_id, posting_date=entry.posting_date.isoformat(),
                status=entry.status.value, memo=entry.memo, line_id=line.line_id,
                line_number=line.line_number, account_id=line.account_id,
                account_name=names[line.account_id], debit_minor=line.debit_minor,
                credit_minor=line.credit_minor, debit_usd=dollars(line.debit_minor),
                credit_usd=dollars(line.credit_minor),
            ))
    _write(output_dir / "journal.csv", (
        "entry_id", "posting_date", "status", "memo", "line_id", "line_number",
        "account_id", "account_name", "debit_minor", "credit_minor", "debit_usd", "credit_usd",
    ), journal_rows)

    _write(output_dir / "ledger.csv", (
        "account_id", "account_name", "posting_date", "entry_id", "line_id", "memo",
        "debit_minor", "credit_minor", "debit_usd", "credit_usd",
        "running_net_debit_minor", "running_balance_usd", "balance_side",
    ), [dict(
        account_id=r.account_id, account_name=names[r.account_id],
        posting_date=r.posting_date.isoformat(), entry_id=r.entry_id,
        line_id=r.line_id, memo=r.memo, debit_minor=r.debit_minor,
        credit_minor=r.credit_minor, debit_usd=dollars(r.debit_minor),
        credit_usd=dollars(r.credit_minor),
        running_net_debit_minor=r.running_net_debit_minor,
        running_balance_usd=dollars(abs(r.running_net_debit_minor)),
        balance_side=("debit" if r.running_net_debit_minor > 0 else
                      "credit" if r.running_net_debit_minor < 0 else "zero"),
    ) for r in ledger])

    trial_rows = [dict(
        account_id=r.account_id, account_name=names[r.account_id],
        debit_balance_minor=r.debit_balance_minor,
        credit_balance_minor=r.credit_balance_minor,
        debit_balance_usd=dollars(r.debit_balance_minor),
        credit_balance_usd=dollars(r.credit_balance_minor),
    ) for r in trial]
    debit_total = sum(r.debit_balance_minor for r in trial)
    credit_total = sum(r.credit_balance_minor for r in trial)
    trial_rows.append(dict(
        account_id="TOTAL", account_name="Trial balance totals",
        debit_balance_minor=debit_total, credit_balance_minor=credit_total,
        debit_balance_usd=dollars(debit_total), credit_balance_usd=dollars(credit_total),
    ))
    _write(output_dir / "trial_balance.csv", (
        "account_id", "account_name", "debit_balance_minor", "credit_balance_minor",
        "debit_balance_usd", "credit_balance_usd",
    ), trial_rows)
