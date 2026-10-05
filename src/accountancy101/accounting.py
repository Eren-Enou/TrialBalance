"""Validation and derived views; no file IO or automatic corrections."""

from datetime import date

from .models import (
    Account, AccountType, EntryStatus, JournalEntry, LedgerRecord, Side,
    TrialBalanceRecord,
)


def validate_accounts(accounts: tuple[Account, ...]) -> None:
    seen = set()
    for account in accounts:
        if not account.account_id.strip() or not account.name.strip():
            raise ValueError("Account ID and name must not be blank")
        if account.account_id in seen:
            raise ValueError(f"Duplicate account ID: {account.account_id}")
        if not isinstance(account.account_type, AccountType):
            raise ValueError("Invalid account type")
        if not isinstance(account.normal_side, Side):
            raise ValueError("Invalid normal side")
        seen.add(account.account_id)


def validate_entry(entry: JournalEntry, accounts: tuple[Account, ...]) -> None:
    """Reject malformed entries; balance alone does not prove correct treatment.

    Drafts must also be structurally valid, but are excluded from the ledger.
    The parent entry supplies the entry ID for every nested line.
    """
    validate_accounts(accounts)
    known_accounts = {account.account_id for account in accounts}
    if not entry.entry_id.strip() or not entry.memo.strip():
        raise ValueError("Entry ID and memo must not be blank")
    if type(entry.posting_date) is not date:
        raise ValueError("Posting date must be a business date")
    if not isinstance(entry.status, EntryStatus):
        raise ValueError("Invalid entry status")
    if len(entry.lines) < 2:
        raise ValueError("An entry requires at least two lines")

    line_ids, line_numbers = set(), set()
    for line in entry.lines:
        if not line.line_id.strip() or line.line_id in line_ids:
            raise ValueError("Blank or duplicate line ID")
        if type(line.line_number) is not int or line.line_number < 1:
            raise ValueError("Line numbers must be positive integers")
        if line.line_number in line_numbers:
            raise ValueError("Duplicate line number")
        if line.account_id not in known_accounts:
            raise ValueError(f"Unknown account: {line.account_id}")
        amounts = (line.debit_minor, line.credit_minor)
        # bool is an int subclass, so use exact type checks for money.
        if any(type(amount) is not int or amount < 0 for amount in amounts):
            raise ValueError("Money must be nonnegative integer cents")
        if (line.debit_minor > 0) == (line.credit_minor > 0):
            raise ValueError("A line must have exactly one positive side")
        line_ids.add(line.line_id)
        line_numbers.add(line.line_number)

    if sum(line.debit_minor for line in entry.lines) != sum(
        line.credit_minor for line in entry.lines
    ):
        raise ValueError(f"Unbalanced entry: {entry.entry_id}")


def derive_ledger(
    accounts: tuple[Account, ...], entries: tuple[JournalEntry, ...]
) -> tuple[LedgerRecord, ...]:
    """Validate the journal, then group posted lines by account.

    Each running balance is debits minus credits. Negative means credit,
    regardless of the account's usual (normal) balance side.
    """
    validate_accounts(accounts)
    entry_ids, line_ids = set(), set()
    for entry in entries:
        validate_entry(entry, accounts)
        if entry.entry_id in entry_ids:
            raise ValueError(f"Duplicate entry ID: {entry.entry_id}")
        entry_ids.add(entry.entry_id)
        for line in entry.lines:
            if line.line_id in line_ids:
                raise ValueError(f"Duplicate journal line ID: {line.line_id}")
            line_ids.add(line.line_id)

    posted = sorted(
        (entry for entry in entries if entry.status == EntryStatus.POSTED),
        key=lambda entry: (entry.posting_date, entry.entry_id),
    )
    rows = []
    for account in sorted(accounts, key=lambda account: account.account_id):
        running = 0
        for entry in posted:
            for line in sorted(entry.lines, key=lambda line: line.line_number):
                if line.account_id == account.account_id:
                    running += line.debit_minor - line.credit_minor
                    rows.append(LedgerRecord(
                        account.account_id, entry.entry_id, line.line_id,
                        entry.posting_date, entry.memo, line.debit_minor,
                        line.credit_minor, running,
                    ))
    return tuple(rows)


def derive_trial_balance(
    accounts: tuple[Account, ...], entries: tuple[JournalEntry, ...]
) -> tuple[TrialBalanceRecord, ...]:
    """Net each account's posted ledger amounts onto its actual balance side."""
    ledger = derive_ledger(accounts, entries)
    balances = {account.account_id: 0 for account in accounts}
    for row in ledger:
        balances[row.account_id] += row.debit_minor - row.credit_minor
    return tuple(
        TrialBalanceRecord(account_id, max(balance, 0), max(-balance, 0))
        for account_id, balance in sorted(balances.items())
    )
