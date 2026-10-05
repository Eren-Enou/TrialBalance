import csv
from dataclasses import replace

import pytest

from accountancy101.csv_output import dollars, export_csv
from accountancy101.sample import ACCOUNTS, ENTRIES


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def test_exports_are_readable_and_preserve_exact_money(tmp_path):
    export_csv(tmp_path, ACCOUNTS, ENTRIES)
    assert {p.name for p in tmp_path.iterdir()} == {
        "accounts.csv", "journal.csv", "ledger.csv", "trial_balance.csv",
    }
    accounts = read_rows(tmp_path / "accounts.csv")
    journal = read_rows(tmp_path / "journal.csv")
    ledger = read_rows(tmp_path / "ledger.csv")
    trial = read_rows(tmp_path / "trial_balance.csv")
    assert len(accounts) == 6
    assert len(journal) == len(ledger) == 10
    assert journal[0]["debit_minor"] == "500000"
    assert journal[0]["debit_usd"] == "5000.00"
    assert ledger[4]["running_balance_usd"] == "4925.00"
    assert ledger[5]["running_net_debit_minor"] == "-500000"
    assert ledger[5]["balance_side"] == "credit"
    assert trial[0]["debit_balance_usd"] == "4925.00"
    assert trial[-1]["account_id"] == "TOTAL"
    assert trial[-1]["debit_balance_minor"] == "580000"
    assert trial[-1]["credit_balance_usd"] == "5800.00"


def test_csv_quoting_preserves_memo_with_comma_quote_and_newline(tmp_path):
    memo = 'Owner says "funding", not revenue\nKeep the source explanation.'
    entry = replace(ENTRIES[0], memo=memo)
    export_csv(tmp_path, ACCOUNTS, (entry,))
    assert read_rows(tmp_path / "journal.csv")[0]["memo"] == memo


def test_invalid_journal_writes_no_output(tmp_path):
    entry = replace(ENTRIES[0], lines=(
        replace(ENTRIES[0].lines[0], debit_minor=1), ENTRIES[0].lines[1],
    ))
    destination = tmp_path / "invalid"
    with pytest.raises(ValueError, match="Unbalanced"):
        export_csv(destination, ACCOUNTS, (entry,))
    assert not destination.exists()


@pytest.mark.parametrize("cents, expected", [(0, "0.00"), (1, "0.01"),
    (-1, "-0.01"), (492500, "4925.00"), (10**18 + 1, "10000000000000000.01")])
def test_dollar_display_never_uses_float(cents, expected):
    assert dollars(cents) == expected
