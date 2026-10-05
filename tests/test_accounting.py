"""Expected values below are handwritten independently of production logic."""

from dataclasses import replace

import pytest

from accountancy101.accounting import derive_ledger, derive_trial_balance, validate_entry
from accountancy101.models import EntryStatus, JournalLine
from accountancy101.sample import ACCOUNTS, ENTRIES


# All monetary constants are integer cents. Do not generate these with the engine.
EXPECTED_BALANCES = {
    "1000": (492_500, 0),
    "3000": (0, 500_000),
    "3100": (20_000, 0),
    "4000": (0, 80_000),
    "5000": (60_000, 0),
    "5100": (7_500, 0),
}
EXPECTED_TRIAL_TOTAL = 580_000
EXPECTED_PROFIT = 12_500
EXPECTED_EQUITY = 492_500
EXPECTED_LEDGER = (
    # account, entry, debit, credit, running debits minus credits
    ("1000", "J001", 500_000, 0, 500_000),
    ("1000", "J002", 80_000, 0, 580_000),
    ("1000", "J003", 0, 60_000, 520_000),
    ("1000", "J004", 0, 7_500, 512_500),
    ("1000", "J005", 0, 20_000, 492_500),
    ("3000", "J001", 0, 500_000, -500_000),
    ("3100", "J005", 20_000, 0, 20_000),
    ("4000", "J002", 0, 80_000, -80_000),
    ("5000", "J003", 60_000, 0, 60_000),
    ("5100", "J004", 7_500, 0, 7_500),
)


def test_five_entries_validate():
    for entry in ENTRIES:
        validate_entry(entry, ACCOUNTS)


def test_every_ledger_movement_and_running_balance():
    ledger = derive_ledger(ACCOUNTS, ENTRIES)
    actual = tuple((r.account_id, r.entry_id, r.debit_minor, r.credit_minor,
                    r.running_net_debit_minor) for r in ledger)
    assert actual == EXPECTED_LEDGER
    assert len({r.line_id for r in ledger}) == 10
    # Journal activity totals differ from trial-balance (net account) totals.
    assert sum(r.debit_minor for r in ledger) == 667_500
    assert sum(r.credit_minor for r in ledger) == 667_500


def test_trial_balance_against_independent_constants():
    trial = derive_trial_balance(ACCOUNTS, ENTRIES)
    balances = {r.account_id: (r.debit_balance_minor, r.credit_balance_minor) for r in trial}
    assert balances == EXPECTED_BALANCES
    assert sum(r.debit_balance_minor for r in trial) == EXPECTED_TRIAL_TOTAL
    assert sum(r.credit_balance_minor for r in trial) == EXPECTED_TRIAL_TOTAL
    profit = balances["4000"][1] - balances["5000"][0] - balances["5100"][0]
    equity = balances["3000"][1] + profit - balances["3100"][0]
    assert profit == EXPECTED_PROFIT
    assert equity == EXPECTED_EQUITY == balances["1000"][0]


def test_order_is_stable_when_entries_and_lines_are_reversed():
    reordered = tuple(replace(e, lines=tuple(reversed(e.lines))) for e in reversed(ENTRIES))
    assert derive_ledger(tuple(reversed(ACCOUNTS)), reordered) == derive_ledger(ACCOUNTS, ENTRIES)


def test_drafts_do_not_enter_ledger_or_trial_balance():
    entries = ENTRIES[:-1] + (replace(ENTRIES[-1], status=EntryStatus.DRAFT),)
    ledger = derive_ledger(ACCOUNTS, entries)
    assert len(ledger) == 8
    assert all(r.entry_id != "J005" for r in ledger)
    trial = {r.account_id: r for r in derive_trial_balance(ACCOUNTS, entries)}
    assert trial["1000"].debit_balance_minor == 512_500
    assert trial["3100"].debit_balance_minor == 0


def test_actual_balance_side_can_differ_from_normal_side():
    # This deliberately hypothetical balanced entry overdraws Checking.
    entry = replace(ENTRIES[2], lines=(
        JournalLine("X1", 1, "5000", debit_minor=100),
        JournalLine("X2", 2, "1000", credit_minor=100),
    ))
    trial = {r.account_id: r for r in derive_trial_balance(ACCOUNTS, (entry,))}
    assert trial["1000"].debit_balance_minor == 0
    assert trial["1000"].credit_balance_minor == 100


def test_zero_activity_includes_all_accounts_with_zero_balances():
    assert derive_ledger(ACCOUNTS, ()) == ()
    trial = derive_trial_balance(ACCOUNTS, ())
    assert len(trial) == 6
    assert all(r.debit_balance_minor == r.credit_balance_minor == 0 for r in trial)


@pytest.mark.parametrize("change, message", [
    ({"debit_minor": 499_999}, "Unbalanced"),
    ({"account_id": "9999"}, "Unknown account"),
    ({"debit_minor": -1}, "integer cents"),
    ({"debit_minor": 500000.0}, "integer cents"),
    ({"debit_minor": True}, "integer cents"),
    ({"debit_minor": 0}, "exactly one positive side"),
    ({"credit_minor": 1}, "exactly one positive side"),
    ({"line_id": ""}, "line ID"),
    ({"line_number": 0}, "positive integers"),
])
def test_invalid_line_rejected(change, message):
    entry = ENTRIES[0]
    invalid = replace(entry, lines=(replace(entry.lines[0], **change), entry.lines[1]))
    with pytest.raises(ValueError, match=message):
        validate_entry(invalid, ACCOUNTS)


@pytest.mark.parametrize("invalid, message", [
    (replace(ENTRIES[0], lines=ENTRIES[0].lines[:1]), "at least two"),
    (replace(ENTRIES[0], entry_id=" "), "Entry ID"),
    (replace(ENTRIES[0], posting_date="2026-01-01"), "business date"),
    (replace(ENTRIES[0], status="posted"), "entry status"),
    (replace(ENTRIES[0], lines=(ENTRIES[0].lines[0],
        replace(ENTRIES[0].lines[1], line_id="J001-L1"))), "line ID"),
    (replace(ENTRIES[0], lines=(ENTRIES[0].lines[0],
        replace(ENTRIES[0].lines[1], line_number=1))), "line number"),
])
def test_invalid_entry_rejected(invalid, message):
    with pytest.raises(ValueError, match=message):
        validate_entry(invalid, ACCOUNTS)


def test_duplicate_entry_rejected_instead_of_double_counted():
    with pytest.raises(ValueError, match="Duplicate entry ID"):
        derive_ledger(ACCOUNTS, ENTRIES + (ENTRIES[0],))


def test_line_ids_are_unique_across_the_journal():
    duplicate = replace(ENTRIES[1], lines=(
        replace(ENTRIES[1].lines[0], line_id="J001-L1"), ENTRIES[1].lines[1],
    ))
    with pytest.raises(ValueError, match="Duplicate journal line ID"):
        derive_ledger(ACCOUNTS, (ENTRIES[0], duplicate))


def test_duplicate_account_rejected():
    with pytest.raises(ValueError, match="Duplicate account ID"):
        derive_ledger(ACCOUNTS + (ACCOUNTS[0],), ENTRIES)
