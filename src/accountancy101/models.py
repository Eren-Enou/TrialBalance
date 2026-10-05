"""Plain immutable records. Monetary amounts are USD integer cents."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class AccountType(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class Side(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class EntryStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"


@dataclass(frozen=True)
class Account:
    account_id: str
    name: str
    account_type: AccountType
    normal_side: Side


@dataclass(frozen=True)
class JournalLine:
    line_id: str
    line_number: int
    account_id: str
    debit_minor: int = 0
    credit_minor: int = 0


@dataclass(frozen=True)
class JournalEntry:
    entry_id: str
    posting_date: date
    memo: str
    lines: tuple[JournalLine, ...]
    status: EntryStatus = EntryStatus.DRAFT


@dataclass(frozen=True)
class LedgerRecord:
    account_id: str
    entry_id: str
    line_id: str
    posting_date: date
    memo: str
    debit_minor: int
    credit_minor: int
    running_net_debit_minor: int


@dataclass(frozen=True)
class TrialBalanceRecord:
    account_id: str
    debit_balance_minor: int
    credit_balance_minor: int
