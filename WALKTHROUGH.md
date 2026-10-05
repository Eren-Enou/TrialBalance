# The five entries, explained

Cedar Desk Services starts with no assets, liabilities or equity. These are
fictional January 2026 transactions. Amounts below are dollars; code stores cents.
The business and its owner are treated separately for bookkeeping.

The accounting equation is **Assets = Liabilities + Owner's equity**.
Assets are resources controlled by the business; liabilities are obligations;
equity is the owner's residual interest. Revenue increases equity through profit;
expenses decrease it. Contributions and drawings change equity without changing profit.

Debit means the left side of an account; credit means the right side. Assets and
expenses normally increase with debits. Liabilities, capital and revenue normally
increase with credits. A normal balance is the usual side, not a ban on the opposite
side. Owner drawings is an equity-reduction account with a normal debit balance.

## J001 — Owner contributes $5,000

**Economic event:** the owner transfers personal money to the business checking account.
Checking is an asset: the business now controls $5,000 more cash, so debit Checking
$5,000. Owner capital is equity: the owner's invested amount increases, so credit
Owner capital $5,000.

**Equation effect:** assets +$5,000; liabilities unchanged; equity +$5,000.
After this entry: $5,000 = $0 + $5,000.
**Profit effect:** none. Funding from the owner is not earned service revenue.

## J002 — Earn and receive $800 for completed services

**Economic event:** services have been completed and the customer pays immediately.
Checking (asset) increases $800: debit Checking. Service revenue (revenue account)
increases $800 because services were earned: credit Service revenue.

**Equation effect:** assets +$800; liabilities unchanged; equity +$800 through profit.
After this entry: $5,800 = $0 + $5,800.
**Profit effect:** +$800. Here earning and cash receipt occur together. Under accrual
accounting, earning and collection need not coincide; this case does not mean every
cash deposit is revenue. Invoice-and-collection exercises are outside this milestone.

## J003 — Pay $600 rent for this period

**Economic event:** the business pays for rental use attributable to this period.
Rent expense (expense account) increases $600: debit Rent expense. Checking (asset)
decreases $600 as money leaves: credit Checking.

**Equation effect:** assets -$600; liabilities unchanged; equity -$600 through expense.
After this entry: $5,200 = $0 + $5,200.
**Profit effect:** -$600; cumulative profit is $200. This entry assumes current-period
rent, not payment for future coverage that might initially be a prepaid asset.

## J004 — Pay $75 for office items consumed this period

**Economic event:** small office items are purchased and consumed during the period.
Office expense (expense account) increases $75: debit Office expense. Checking
(asset) decreases $75: credit Checking.

**Equation effect:** assets -$75; liabilities unchanged; equity -$75 through expense.
After this entry: $5,125 = $0 + $5,125.
**Profit effect:** -$75; cumulative profit is $125. Consumption is an explicit fact
of this exercise. Do not infer that all office purchases are immediately expenses;
equipment or unconsumed supplies can require a different treatment.

## J005 — Owner withdraws $200 for personal use

**Economic event:** the owner removes business cash for personal use.
Checking (asset) decreases $200: credit Checking. Owner drawings (equity-reduction
account) increases $200: debit Owner drawings. Increasing this debit-balance account
reduces total owner's equity; it does not increase business expenses.

**Equation effect:** assets -$200; liabilities unchanged; equity -$200 through drawings.
After this entry: $4,925 = $0 + $4,925.
**Profit effect:** none. Profit stays $125. Personal spending is not a business expense
merely because it was paid from the business account. This is a simplified owner-capital
teaching model, not a tax or entity-specific distribution rule.

## Trace the journal into the ledger

Each journal entry has a header and at least two account lines. The ledger reorganizes
those same posted lines by account; it does not create new transactions. In Checking:

| Entry | Debit | Credit | Running debit balance |
|---|---:|---:|---:|
| J001 | 5,000.00 | — | 5,000.00 |
| J002 | 800.00 | — | 5,800.00 |
| J003 | — | 600.00 | 5,200.00 |
| J004 | — | 75.00 | 5,125.00 |
| J005 | — | 200.00 | 4,925.00 |

The other five accounts each have one movement. Their ending balances form the
remaining trial-balance rows. Drafts are excluded because they are not posted.
All entries here are posted. Ordering uses posting date, entry ID, then line number.

## Hand-check the trial balance and equation

| Account | Debit balance | Credit balance |
|---|---:|---:|
| Checking | 4,925.00 | — |
| Owner capital | — | 5,000.00 |
| Owner drawings | 200.00 | — |
| Service revenue | — | 800.00 |
| Rent expense | 600.00 | — |
| Office expense | 75.00 | — |
| **Total** | **5,800.00** | **5,800.00** |

Compute independently on paper:

- Cash: $5,000 + $800 − $600 − $75 − $200 = **$4,925**.
- Profit: $800 − $600 − $75 = **$125**.
- Equity: $5,000 contribution + $125 profit − $200 drawings = **$4,925**.
- Equation: $4,925 assets = $0 liabilities + $4,925 equity.
- Trial debits: $4,925 + $200 + $600 + $75 = **$5,800**.
- Trial credits: $5,000 + $800 = **$5,800**.

These are pre-closing balances: revenue, expenses and drawings remain in their
own accounts. The equation includes their effect on equity; no closing entries are
required for this exercise. Total debit/credit journal activity is $6,675 each,
whereas the trial balance nets activity by account and totals $5,800 each.

## Read the code without losing the accounting

Start with `sample.py`: identify each economic event and both account movements.
In `validate_entry`, notice that each line needs exactly one positive side and
each entry needs equal debit/credit totals. These checks cannot tell whether an
owner withdrawal was wrongly classified as an expense; use the economic facts.

In `derive_ledger`, drafts are removed and each posted cash line changes the
running balance by `debit_minor - credit_minor`. The same convention works for
every account; capital and revenue have negative net-debit balances.

In `derive_trial_balance`, a positive net becomes a debit balance and a negative
net becomes a credit balance. The account's normal side does not force the result.
In `tests/test_accounting.py`, compare handwritten `EXPECTED_LEDGER` and
`EXPECTED_BALANCES` to the output. Those constants are independent expectations,
not values copied from production calculations at test runtime.

Try explaining J005 before looking at its lines: which resource leaves, whose
equity changes, and why profit stays the same? This manual question preserves
the learning objective without introducing a learning UI.
