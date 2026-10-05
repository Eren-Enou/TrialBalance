"""Five hand-written events: zero opening balances, no random generation."""

from datetime import date

from .models import Account, AccountType, EntryStatus, JournalEntry, JournalLine, Side


ACCOUNTS = (
    Account("1000", "Checking", AccountType.ASSET, Side.DEBIT),
    Account("3000", "Owner capital", AccountType.EQUITY, Side.CREDIT),
    Account("3100", "Owner drawings", AccountType.EQUITY, Side.DEBIT),
    Account("4000", "Service revenue", AccountType.REVENUE, Side.CREDIT),
    Account("5000", "Rent expense", AccountType.EXPENSE, Side.DEBIT),
    Account("5100", "Office expense", AccountType.EXPENSE, Side.DEBIT),
)

ENTRIES = (
    JournalEntry("J001", date(2026, 1, 1), "Owner contributes $5,000", (
        JournalLine("J001-L1", 1, "1000", debit_minor=500_000),
        JournalLine("J001-L2", 2, "3000", credit_minor=500_000),
    ), EntryStatus.POSTED),
    JournalEntry("J002", date(2026, 1, 2), "Earn and receive $800 for completed services", (
        JournalLine("J002-L1", 1, "1000", debit_minor=80_000),
        JournalLine("J002-L2", 2, "4000", credit_minor=80_000),
    ), EntryStatus.POSTED),
    JournalEntry("J003", date(2026, 1, 3), "Pay $600 rent for this period", (
        JournalLine("J003-L1", 1, "5000", debit_minor=60_000),
        JournalLine("J003-L2", 2, "1000", credit_minor=60_000),
    ), EntryStatus.POSTED),
    JournalEntry("J004", date(2026, 1, 4), "Pay $75 for office items consumed this period", (
        JournalLine("J004-L1", 1, "5100", debit_minor=7_500),
        JournalLine("J004-L2", 2, "1000", credit_minor=7_500),
    ), EntryStatus.POSTED),
    JournalEntry("J005", date(2026, 1, 5), "Owner withdraws $200 for personal use", (
        JournalLine("J005-L1", 1, "3100", debit_minor=20_000),
        JournalLine("J005-L2", 2, "1000", credit_minor=20_000),
    ), EntryStatus.POSTED),
)
