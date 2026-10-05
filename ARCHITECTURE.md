# Accountancy101 — Milestone 1: research and architecture

Status: architecture approved; Milestone 2 authorized on October 4, 2026.
Prepared October 4, 2026. Implementation is limited to the five-entry kernel.

Approved decisions: Cedar Desk Services; USD; simplified accrual accounting;
U.S. accounting terminology; one checking account; detailed early explanations;
terminal learning prompts plus XLSX inspection workbooks in later milestones.
Tax and jurisdiction-specific reporting rules are excluded. The original proposal
below is retained as the roadmap; its approval questions have been answered.

## A. Recommended architecture

Build a local Python package with a small command-line interface, readable CSV datasets, XLSX inspection workbooks, and Markdown explanations. Use ordinary functions and a few typed data classes. No web application, database server, authentication, cloud service, or framework is needed.

The central rule is: **economic events, accounting entries, bank activity, and reconciliation decisions are different records**. Preserve their relationships without collapsing them into one spreadsheet. An invoice creates revenue and a receivable; its later collection creates cash and reduces that receivable. The bank sees the collection, not the invoice.

### Proposed fictional business and scope

Use **Cedar Desk Services**, a fictional owner-operated consulting business. Initial assumptions to confirm: USD, one checking account, simplified accrual accounting, calendar months, no inventory, employees, sales taxes, foreign currencies, or income-tax calculations. These are teaching simplifications, not a claim of compliance with a particular reporting framework.

Accrual accounting recognizes revenue when earned and expenses when incurred, rather than simply when money moves. Start with owner contributions, completed cash services, rent, and expenses. Add customer invoices and supplier bills once basic posting is understood. Use a clearly defined opening position and dated periods; generate transactions near month-end and later clearing activity when timing exercises begin.

### Components and dependency rules

| Component | Responsibility | Must not do |
|---|---|---|
| `models.py` | Typed records, IDs, enums, schema contracts | Import pandas or contain spreadsheet formatting |
| `accounting.py` | Validate entries; derive ledger, balances and accounting effects | Read bank files or guess transactions from descriptions |
| `io.py` | Read/write CSV and XLSX; retain source provenance | Decide accounting treatment |
| `normalize.py` | Explicit source mappings, dates, amounts, descriptions; rejected-row report | Silently discard or repair financial facts |
| `synthetic.py` | Generate events, intended journals, clearing schedules and private labels | Supply private truth to the matcher |
| `reconcile.py` | Produce candidates, accepted matches, ambiguities and exceptions | Post adjustments or read answer labels |
| `explanations.py` | Shared explanation records and reviewed scenario templates | Reimplement ledger calculations |
| `learning.py` | Present evidence; collect answers; reveal shared explanations | Change the learner's books to the answer automatically |
| `reports.py` | Render accounting results, exception reports and workbooks | Recalculate accounting rules independently |
| `cli.py` | Connect commands, paths and explicit user decisions | Become the accounting engine |

Keep these as single files initially; split a module only when its size or responsibilities justify it. Modules are organizational boundaries, not a request for plugin systems, inheritance hierarchies, or repositories/interfaces for every object.

Typical workflow:

```text
Business events -> intended journal entries -> validated postings -> ledger -> reports
       |
       +-> settlement schedule -> bank statement

Clean records -> scenario transformations -> learner books and bank exports
                                                    |
                                      import -> normalize -> reconcile
                                                    |
                              candidates / exceptions / proposed adjustments
                                                    |
                              learner answer -> explanation -> reviewed posting

Private scenario labels ---------------------------------> evaluation only
```

A journal is the chronological record of accounting entries; a ledger groups the posted lines by account. A trial balance lists account balances and checks that total debit balances equal total credit balances. These are related views of the same postings, not separately edited sources of truth. See [OpenStax's accounting-cycle introduction](https://openstax.org/books/principles-financial-accounting/pages/3-3-define-and-describe-the-initial-steps-in-the-accounting-cycle).

### Libraries

| Library | Recommendation and purpose |
|---|---|
| Python standard library | `dataclasses` and `enum` for clear records; `datetime` for business dates; `pathlib`, `csv`, `json`, `hashlib`, `random`, and `argparse` for local files, manifests, repeatable generation, and CLI. These keep the core understandable. [Data classes documentation](https://docs.python.org/3/library/dataclasses.html). |
| `decimal` (standard library) | Parse decimal strings and apply explicit rounding when calculations need fractional cents. Store posted USD amounts as integer cents. Never construct monetary Decimal values from binary floats. [Decimal documentation](https://docs.python.org/3/library/decimal.html). |
| `pandas` | Tabular ingestion, normalization, joins, grouping, and export. Specify ID/date/money conversion rules instead of relying on inference. Use merge validation and indicators to expose unexpected multiplicity and unmatched rows. Keep accounting calculations usable without DataFrames. [Excel reading](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html), [merge documentation](https://pandas.pydata.org/docs/reference/api/pandas.merge.html). |
| `openpyxl` | XLSX worksheets, numeric formats, frozen headers, filters, and reader-friendly styles; also the initial pandas XLSX engine. It does not calculate spreadsheet formulas, so export Python-computed totals as authoritative values. Optional formulas may illustrate manual checks. [Formula limitations](https://openpyxl.readthedocs.io/en/latest/simple_formulae.html). |
| `pytest` | Small example-based tests and parametrized scenario tests. Introduce with the first accounting kernel. [Parametrization documentation](https://docs.pytest.org/en/stable/how-to/parametrize.html). |
| `RapidFuzz` — later | Description similarity after exact and normalized matching are reliable. Choose and record the scorer and preprocessing explicitly. Similarity is evidence, not proof of an accounting match. [Official documentation](https://rapidfuzz.github.io/RapidFuzz/), [candidate extraction](https://rapidfuzz.github.io/RapidFuzz/Usage/process.html). |
| `Hypothesis` — later | Generate edge cases for balance conservation, serialization round trips, and non-overlapping allocations. Add after readable example tests exist. [Official introduction](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html). |

Do not initially add Faker, NumPy as a direct dependency, Pydantic, SQLAlchemy, a task queue, or an LLM dependency. A small hand-written customer/vendor catalog teaches more than random identities. Local explanations can use reviewed templates. Choose a supported Python version and lock tested dependency versions when implementation begins; no version installation is part of this milestone. Initial runtime dependencies are only pandas and openpyxl; pytest is a development dependency.

### Data conventions

- Every dataset has a schema version and every record has a stable ID. IDs are strings, including account codes and references with leading zeros.
- One currency initially. Monetary columns use explicit integer-cent names such as `debit_minor`, not ambiguous `amount`. CSV integer cents are canonical; XLSX may add dollar display columns. Do not silently round excess precision on import.
- Canonical dates use `YYYY-MM-DD`. Distinguish economic/service date, book posting date, bank posting date, and bank value date; the latter is the bank's effective date where supplied.
- Debit and credit columns are nonnegative. Each journal line has exactly one positive side. Bank and book cash movements use the business perspective: incoming cash positive, outgoing cash negative. A bank's debit/credit labels require an explicit adapter.
- Preserve raw source values and provenance before normalization. Reject malformed inputs into a report with file, sheet/row, field, raw value, and reason. Never fill missing money with zero.
- A manifest records business assumptions, period, currency scale, rounding policy, seed, generator/rule/schema versions, source hashes, and opening balances. Published output is written to a new run directory rather than overwriting prior runs.

### Initial data model

Tables are separate CSV files and corresponding workbook sheets. The model defines expansion points, not an instruction to implement all entities immediately.

| Record and grain | Fields and relationships | Important rules |
|---|---|---|
| **Account**, one chart-of-accounts row | `account_id`, `code`, `name`, `type` (asset/liability/equity/revenue/expense), `normal_side`, `statement_group`, `active`; later `contra_of_account_id` | Code unique. Normal side is a display/interpretation rule, not a prohibition on opposite-side movements. A contra account offsets another account, e.g. accumulated depreciation offsets equipment. |
| **BusinessEvent**, one economic occurrence | `event_id`, `event_type`, `economic_date`, `counterparty_id`, `document_ref`, `description`, `gross_minor`, `currency`, `related_event_id`, `service_period_start/end` when relevant | Positive magnitude; type defines meaning. Parent/related links distinguish invoice, collection, refund and return. Later add line-item and allocation tables rather than stuffing invoice detail into text. |
| **JournalEntry**, one header | `entry_id`, `posting_date`, `memo`, `status` (draft/posted), `entry_kind` (opening/ordinary/adjusting/correcting/reversing), `reverses_entry_id`, `origin`, `rule_id/version` | Posted entries immutable. Corrections are new entries with links. Later support explicit event-to-entry links for batched or composite events. |
| **JournalLine**, one account-side movement | `line_id`, `entry_id`, `line_number`, `account_id`, `debit_minor`, `credit_minor`, optional `event_id`, `counterparty_id`, `document_ref`, later `settlement_id` | Unique line ID and `(entry_id, line_number)`; foreign keys valid; entry has at least two lines; sum debits equals sum credits; one positive side per line. |
| **BankStatement**, one account/period | `statement_id`, `bank_account_id`, `cash_account_id`, `period_start/end`, `currency`, `opening_minor`, `closing_minor`, `source_file_id` | Opening plus signed movements equals closing, unless this is an explicitly labeled corrupted-import exercise. |
| **BankRecord**, one statement movement | `bank_record_id`, `statement_id`, `bank_posting_date`, optional `value_date`, `signed_amount_minor`, `raw_description`, `normalized_description`, `reference`, `counterparty`, `source_row_id` | Provider reference may be absent or repeated. Imported row identity is not proof of transaction uniqueness. No private event IDs in matcher-visible exports. |
| **LedgerRecord**, one derived posted journal line | `line_id`, `entry_id`, `account_id`, `posting_date`, `debit_minor`, `credit_minor`, `running_net_debit_minor` | Derived from posted entries, never independently edited. Stable order is posting date then entry/line order. Opening positions come from an opening journal, not a second hidden balance. |
| **BookCashMovement**, one derived settlement movement | `book_record_id`, `cash_account_id`, `posting_date`, `signed_amount_minor`, `document_ref`, `description`; child link rows identify source journal lines | Cash amount equals debit minus credit on the cash account. Initially one cash line per movement; later explicit settlement IDs group related cash lines. Never infer grouping solely from identical amounts/descriptions. |
| **ReconciliationRun**, one execution | `run_id`, account/currency/period, `input_hashes`, `rules_version`, `config`, `book_closing_minor`, `bank_closing_minor`, adjusted balances, `residual_minor` | Freeze inputs, assumptions and cutoffs. Run can finish with unresolved differences. |
| **MatchGroup**, one candidate or accepted group | `match_id`, `run_id`, `stage`, `status` (candidate/accepted/rejected/ambiguous), `score`, `evidence`, `runner_up_gap`, `decision_origin` | Candidate relationships are not automatically consumed. Evidence states amount totals, references, date gaps and alternatives. |
| **MatchMember**, one allocation to one group | `match_id`, `side` (book/bank), `record_id`, `allocated_signed_minor` | Supports one-to-one, many-to-one, and later partial settlements. Accepted allocations cannot exceed or reuse the available amount. Preserve sign and account/currency. |
| **ReconciliationException**, one observed issue | `exception_id`, `run_id`, affected record links, `category`, `status`, `evidence`, `hypothesis`, `proposed_entry_id`, `action` (timing/book correction/bank inquiry/investigate) | Hypotheses may remain unknown. An exception is not necessarily an accounting error. Classification and match confidence are separate. |
| **SyntheticDiscrepancy**, one private scenario label | `scenario_id`, `kind`, affected truth/observed ID link tables, `transformation`, before/after values or snapshot references, `expected_disposition`, `expected_rule_id`, `detectable_from`, `required_evidence`, `expected_correction_spec` | Includes legitimate timing and normal split-payment scenarios. Labels need not map one-to-one to report rows. Keep withheld evidence explicit. |
| **Explanation**, one shared accounting assessment | `assessment_id`, `rule_id/version`, evidence references, economic story, account effects, journal proposal, ledger changes, statement effects, `requires_entry` (yes/no/unknown), assumptions, rationale | Derived account/ledger effects use accounting functions. Narratives reference those results. An approved synthetic answer may use private truth; ordinary assessment cannot. |
| **LearningAttempt**, one learner response | `attempt_id`, prompt/scenario reference, response, chosen accounts/debits/credits/disposition, timestamps, reveal state, explanation version | Store separately from journals. Compare normalized lines, allowing equivalent valid entries and supported reasoning. |

Relationship summary: accounts have many journal lines; entries have many lines; events can lead to several entries over their life; cash movements link to cash ledger lines; statements have many bank rows; match groups have many members on both sides; exceptions and private labels link to sets of records. No database is needed to enforce these relationships: explicit validation functions check them at file boundaries.

Initial chart: 1000 Checking; 1100 Accounts receivable (customer amounts owed); 1200 Prepaid insurance; 1500 Equipment; 1590 Accumulated depreciation; 2000 Accounts payable (supplier amounts owed); 2100 Accrued expenses; 3000 Owner capital; 3100 Owner drawings; 4000 Service revenue; 4100 Interest income; 5000 Rent expense; 5100 Office expense; 5200 Bank fees; 5300 Insurance expense; 5400 Depreciation expense. Add only accounts required by each milestone. Drawings reduce owner equity; they are not business expenses.

### Proposed project structure

```text
Accountancy101/
  ARCHITECTURE.md                 # this proposal
  README.md                      # later: run instructions and learning sequence
  pyproject.toml                 # later: package/dependencies/test configuration
  src/accountancy101/
    __init__.py
    models.py
    accounting.py
    io.py
    normalize.py
    synthetic.py
    reconcile.py
    explanations.py
    learning.py
    reports.py
    cli.py
  scenarios/                     # reviewed scenario definitions, no learner answers
  lessons/                       # prompts and concept notes
  data/
    raw/<import_id>/             # unchanged imported files
    runs/<dataset_id>/
      manifest.json
      truth/                     # clean books, events, settlements, private labels
      observed/                  # learner-visible books and bank records
  outputs/<run_id>/               # matches, exceptions, reports, inspection.xlsx
  learning_attempts/              # local answer/reveal history
  tests/
    fixtures/                    # tiny independently checked examples
    test_accounting.py
    test_io.py
    test_normalize.py
    test_synthetic.py
    test_reconcile.py
    test_learning.py
  docs/
    accounting_glossary.md
    data_dictionary.md
    manual_checks.md
```

This is a target structure. Create files as they become useful, not empty scaffolding for every future feature. The truth folder is a logical isolation boundary in a single-user local project, not a security boundary. Ordinary CLI/report paths must exclude it unless explicitly revealing answers or evaluating tests.

### Synthetic-data strategy

1. **Begin with hand-checked cases.** Create an opening journal and a few explicit business events. Write expected balances by hand before trusting generated ones.
2. **Generate events with business constraints.** Use a local seeded random generator, a small counterparty catalog, recurring rent, customer terms, invoice/payment links, and reasonable clearing delays. A receipt cannot settle an invoice that does not exist; allocations cannot exceed unpaid balances. Specify whether overdrafts are permitted rather than deleting awkward transactions.
3. **Post intended accounting through reviewed rules.** Each event type has an explicit entry specification and explanation. Validate journals; derive ledgers and trial balances. This forms the intended books for that scenario's accounting stage.
4. **Generate bank settlement independently of ledger formatting.** Only settled cash movements appear at their bank posting dates. Generate genuine bank-originated events such as fees and interest. Their intended book entries belong in truth; withholding them from observed books creates the exercise.
5. **Preserve clean snapshots.** Hash baseline files. Apply named transformations only to copied observed data. Record stable mappings from truth IDs to observed IDs privately, including deleted rows and inserted duplicates.
6. **Apply discrepancies at the correct layer.** Missing postings omit a whole balanced entry. Duplicate postings duplicate a complete entry with new IDs. Misclassification changes the account while retaining balance. A book amount transposition alters both sides of a simple entry. A malformed imported row is a separate ingestion exercise, not a normal balanced journal.
7. **Recompute dependent observed totals correctly.** A duplicated book entry changes the observed cash ledger. A deliberately missing bank-export row leaves the original statement closing balance, exposing a completeness failure. A true bank error changes the bank's records and balance and is labeled separately.
8. **Keep answer access explicit.** The matcher takes only observed records/configuration. Evaluation takes matcher output plus private correspondence and scenario labels. Learning mode loads answers only on reveal. Exported IDs must not encode error type or provide a shared private matching key.
9. **Expand difficulty gradually.** Single-issue fixtures, several independent issues, then deliberate interactions and ambiguous cases. Use separate development seeds and held-out scenario compositions; a seed alone is insufficient for reproducibility, so record versions and policies too.

Scenario treatments to teach:

| Scenario | Observable evidence and disposition | Expected treatment under stated assumptions |
|---|---|---|
| Outstanding check | Book payment before cutoff; bank clears later | Timing item; no new entry if original payment is correct |
| Deposit in transit | Valid book receipt/deposit before cutoff; bank credits later | Timing item; no new entry if correctly recognized |
| Unrecorded bank fee | Bank withdrawal plus fee evidence; no book entry | Debit Bank fees, credit Checking |
| Unrecorded interest | Bank credit plus interest evidence | Debit Checking, credit Interest income |
| Duplicate book posting | One source event, two postings; distinguish from repeated legitimate purchases | Reverse only the confirmed duplicate entry; preserve both audit links |
| Transposed amount | Source document supports correct figure; amount discrepancy alone is insufficient | Correct the difference or reverse/repost; validate both sides |
| Missing book transaction | Bank movement and supporting document, absent book event/posting | Record the actual event using its substance; do not default every deposit to revenue |
| Incorrect account classification | Amount and cash can reconcile while another account is wrong | Reclassify affected noncash accounts; bank matching alone may not detect it |
| Split payments or batched deposits | Allocation or deposit evidence supports multiple components | Can be normal settlement; no automatic error or adjustment |
| NSF customer payment | Bank reverses a previously recorded collection; customer still owes | Debit Receivable, credit Checking; any bank fee is separate. NSF means insufficient funds, not automatically bad debt |
| Accrual | Expense incurred but unpaid, supported by period evidence | Debit relevant Expense, credit Accrued expenses; no current cash movement |
| Prepaid insurance | Payment covers future periods; coverage schedule available | Initially debit Prepaid insurance, credit Checking; recognize consumed coverage via debit Insurance expense, credit Prepaid insurance |
| Depreciation | Equipment cost and usage/life assumptions | Debit Depreciation expense, credit Accumulated depreciation; noncash allocation, not a guessed market-value loss |
| Cutoff issue | Service, document, posting and settlement dates straddle periods | Diagnose recognition timing using evidence; do not solve by forcing bank and book dates to agree |

Outstanding payments/deposits differ from unrecorded book items. Bank-side timing items reconcile the statement; bank fees and other missing book items affect the cash ledger. [ACCA's FA1 examiner report](https://www.accaglobal.com/content/dam/acca/global/PDF-students/fia/examreports/FA1/FA1%20S23-A24%20examiner%27s%20report.pdf) illustrates that distinction. [OpenStax's bank reconciliation chapter](https://openstax.org/books/principles-financial-accounting/pages/8-6-define-the-purpose-of-a-bank-reconciliation-and-prepare-a-bank-reconciliation-and-its-associated-journal-entries) is the suggested accompanying reading.

### Reconciliation strategy in stages

Reconciliation means explaining differences between two records and establishing an agreed balance. Matching rows is only part of that process.

First validate statement completeness and derive book cash from posted entries. Scope by bank account, currency and period. Carry prior-period outstanding items into the current run and consult later clearing evidence when supplied. Exclude post-cutoff activity from closing balances even when using it to explain a timing item. A record unmatched in the available window is unresolved, not proven missing.

| Stage | Candidate rule | Acceptance/review policy |
|---|---|---|
| 1. Exact | Same signed cents, account/currency, date and reliable reference | Accept only unique, mutually consistent pairs. Same amount/date alone remains weaker evidence. Blank references do not equal evidence. |
| 2. Normalized | Same facts after explicit whitespace/case/reference formatting and source mapping | Retain originals and normalization log. Do not remove meaningful invoice/check numbers or signs. |
| 3. Date tolerance | Exact signed amount and compatible reference/counterparty within a configurable window | Start with an illustrative 3-calendar-day window, not a universal bank rule. Record actual date gap; repeated amounts create ambiguity. |
| 4. Description similarity | Amount/sign/account/currency pass hard gates; date is plausible; rank normalized descriptions using RapidFuzz | Initially propose for review only. A similar description cannot override a conflicting strong reference. |
| 5. Duplicate handling | Inspect duplicate source rows, repeated references and repeated journal postings | Run multiplicity checks before accepting earlier stages. Never deduplicate solely on amount/date/text. Preserve repeated legitimate rent/payment examples as negative controls. |
| 6. Split/group matching | Small, bounded groups have exact signed total and supporting settlement evidence | Start with groups of 2–3 within a documented date window. Search both directions. If several groupings fit, abstain; do not greedily take the first subset sum. |
| 7. Confidence and review | Preserve feature values, stage, conflicts, alternatives and explanations | Separate match score, accounting hypothesis and human decision. Acceptance cannot consume the same amount twice. |

For pandas joins, use `validate='one_to_one'` only after establishing unique keys and `indicator=True` to expose leftovers. Never allow a many-to-many join to multiply rows and call the result reconciled. Missing join keys need explicit handling: pandas can match null keys to each other. [pandas merge documentation](https://pandas.pydata.org/docs/reference/api/pandas.merge.html).

For later fuzzy ranking, an illustrative heuristic is `score = 60R + 25D + 15T`, where R is a reliable matching-reference indicator, D is date closeness within the configured window, and T is normalized text similarity scaled to 0–1. Signed amount/account/currency equality is a hard gate, not a compensating score. Penalize ambiguity by routing to review rather than hiding it. This heuristic is a proposed design, not an estimated probability or empirically validated threshold. Initially auto-accept only unambiguous exact/normalized cases; fuzzy and group matches require review. Later calibrate thresholds and the best-versus-runner-up margin on held-out labels, emphasizing false-match avoidance. Conflicting strong references always block acceptance.

Group proposals and one-to-one proposals must be considered together where they compete. Commit only conflict-free accepted allocations; leave uncertain connected sets for review. Partial payment matching eventually allocates portions explicitly and carries the unallocated remainder. Net processor deposits require documented gross receipts and fees; do not create a silent monetary tolerance.

After matching, classify unmatched evidence as timing, book omission/error, possible bank error, or unresolved. Generate proposed journal entries only when supporting facts identify the accounts. Book corrections remain drafts until reviewed. Bank errors generally require inquiry and a reconciling item, not a fabricated company expense.

Produce a reconciliation worksheet with:

- Statement opening/closing and book opening/closing balances.
- Adjustments on the appropriate side, each linked to evidence and a proposed entry if applicable.
- Adjusted bank and book balances, residual difference, unmatched rows, ambiguities and stale timing items.
- Separate counts for matched, timing, needs-entry, rejected and unresolved items.

Hand-check example, assuming valid original checks/deposits: statement cash $9,200 + $1,000 deposit in transit − $300 outstanding check = $9,900 adjusted bank cash. Book cash $9,930 − $30 unrecorded fee = $9,900 adjusted book cash. The fee entry is debit Bank fees $30 / credit Checking $30. The deposit and check require no second posting. This numerical example is an original test fixture, not a quoted exercise.

### Learning mode: shared logic and visible reasoning

Use a prompt → answer → compare → reveal → optional reviewed posting workflow. The learner sees the transaction/source evidence, accounts available, and a blank treatment prompt before the explanation or expected journal. Ask what happened, whether cash moved, which accounts changed, debit/credit amounts, statement effects, and whether a new entry is necessary.

`accounting.py` calculates the proposed entry's account changes, ledger effects and statement totals once. `explanations.py` attaches the reviewed economic rationale. Both normal reports and the lesson renderer consume that same assessment. Scenario definitions supply facts and teaching prompts; they do not implement another posting engine. Evidence-limited ordinary assessments say “unknown” where private scenario truth would reveal more.

Example: services worth $800 were completed and invoiced; payment comes later. The invoice proposal debits Receivable $800 and credits Service revenue $800. The ledger shows both lines; profit and receivables rise, but cash has not moved. Collection later debits Checking and credits Receivable, without recognizing revenue a second time. For a full indirect cash-flow statement, working-capital adjustments explain why profit and cash differ; do not equate journal-level cash labels with a complete statement.

Debits and credits mean the two sides of an entry, not universally “increase” and “decrease.” Assets and expenses usually have debit balances; liabilities, equity and revenue usually have credit balances. Teach the account type and economic event alongside the sign. A proposed entry can balance and still be wrong.

Learner responses may include “no entry,” “need more evidence,” equivalent balanced entry layouts, and supported alternatives under stated assumptions. Feedback should distinguish arithmetic errors, account selection, recognition timing and unsupported certainty. Revealing an answer records an attempt; it never changes a posted ledger. A later explicit posting step uses the same validator and records its source explanation/version.

## B. Incremental milestone plan

| Milestone | Software concepts practiced | Accounting concepts practiced | Concrete artifact | Manual inspection and exit check |
|---|---|---|---|---|
| **1. Research and architecture — this milestone** | Boundaries, data contracts, dependency selection | Events versus journals versus bank records; terminology | This design and decisions for review | Trace an invoice/collection and the $30-fee example; confirm scope assumptions |
| **2. A tiny accounting kernel** | Dataclasses, pure functions, integer amounts, pytest | Debit/credit, account types, double entry, ledger and trial balance | Five hand-written entries, ledger CSV and trial-balance CSV | Hand-calculate each account and compare totals; invalid/unbalanced entries rejected |
| **3. Reliable CSV/XLSX round trip** | pandas/openpyxl, explicit types, normalization, provenance | Source documents, completeness and audit trail | CSV input plus inspection workbook and rejected-row report | Compare IDs, dates and exact cents after reimport; test leading zeros and a deliberately invalid amount |
| **4. A clean synthetic month** | Seeded generation, manifests, relationships | Ordinary accrual transactions, invoice/collection, bills/payments, opening/closing balances | Events, intended journals, bank statement, trial balance and README of assumptions | Trace selected events to journal and ledger; independently sum cash; reproduce the same logical data with same manifest |
| **5. Exact bank reconciliation plus first lesson** | Joins, multiplicity checks, staged results, input/reveal flow | Deposits/checks, timing versus missing entries, bank fees | A clean and a three-issue dataset, reconciliation worksheet, one ask-before-reveal lesson | Use the hand-worked $9,900 example; confirm only the fee needs a book entry and reveal does not post it |
| **6. Difficult matching and measurable detection** | Date windows, RapidFuzz, bounded group search, scoring, allocations | Repeated payments, splits, duplicate postings, NSF, investigation | Candidate/exception reports, private labels and evaluation metrics | Inspect competing candidates and a false-match trap; verify no row/amount is consumed twice; review held-out outcomes |
| **7. AP/AR and richer learning** | Lifecycle state, allocation tables, answer equivalence | Receivables/payables, aging, partial settlement, refunds and bad-debt distinctions | Customer/vendor detail, aging reports and several reviewed lesson sets | Tie subledger totals to control accounts; follow one invoice through partial payments; compare learner reasoning before revealing |
| **8. Month-end close and statements** | Period rules, schedules, reusable aggregations, property tests | Accruals, prepayments, depreciation, cutoff; income statement, balance sheet, cash-flow bridge | Adjustment proposals, pre/post-adjustment trial balances, statements and close checklist | Recalculate one schedule; verify assets = liabilities + equity including current profit; tie cash change to cash-flow report; closed-period corrections are explicit |
| **9. Controls and audit exercises** | Change logs, validation rules, reproducible evidence bundles | Authorization, completeness, accuracy, duplicate detection; audit assertions | Exceptions tied to evidence, simulated review log and control exercises | Trace evidence both directions, distinguish anomaly from proven misstatement; test a control that misses an intentional error |
| **10. Jurisdiction-specific tax exercises — optional** | Effective-dated rules, source citation, policy/version handling | Book versus tax differences and jurisdiction-specific treatment | A narrow documented tax exercise and book-to-tax bridge | Rework against the chosen authority's current guidance and tax year; do not add generic tax rules before jurisdiction/entity are selected |

AP/AR means accounts payable/accounts receivable. A subledger contains customer/vendor detail; its total should agree with the corresponding general-ledger control account. Aging groups unpaid amounts by due-date age. Month-end close is the review and adjustment process used to produce period reports. Audit assertions are claims such as existence, completeness and correct period recognition; an automated flag is evidence for investigation, not an audit opinion.

Each milestone should remain small enough to inspect. Later statements and tax are extensions, not prerequisites for a useful learning project. Introduce review logs locally; do not build authentication merely to simulate segregation of duties.

### Testing strategy

**Unit examples:** test money/date parsing, normal-side display, balanced-entry validation, unknown accounts, duplicate line IDs, deterministic ledger ordering, opening journals, drafts excluded from posted reports, missing references, date-window boundaries and normalization preserving meaningful digits. Confirm rejected rows remain visible.

**Independent accounting fixtures:** expected amounts are handwritten, not computed by the same function being tested. For the first five entries, specify every expected ending balance. A second independent method can sum journal cash lines and compare with the report. An invariant alone cannot detect a balanced posting to the wrong account.

**Accounting invariants:**

- Each posted entry has equal total debits and credits and valid one-sided lines; total posted ledger debits equal credits.
- Every posted line appears once in the derived ledger; drafts contribute nothing. Balance = opening movements + period movements under the selected sign convention.
- Trial-balance debit balances equal credit balances. Later, assets equal liabilities plus equity, including current-period income and drawings with consistent closing treatment.
- Statement opening cash + signed bank rows = statement closing cash; the book cash view ties to the cash ledger.
- Accepted match allocations do not overlap or exceed source amounts; exact/group match sums agree. Unmatched remainders conserve amounts.
- Receivable/payable detail agrees to control accounts; settlement allocations do not exceed outstanding balances unless an explicit credit/overpayment model allows it.
- Schedule allocations conserve original cost and respect coverage/life assumptions; cash-flow opening + net change = closing cash.
- Reviewed corrections produce expected changes and remain traceable; applying a transformation or posting operation twice is rejected or explicitly idempotent, never a silent duplicate.

**Synthetic-ground-truth tests:** scenario labels specify expected affected record sets, accepted match membership, exception category, disposition and correction specification. Evaluate match accuracy separately from discrepancy classification. Measure precision (how many accepted flags/matches are correct), recall (how many expected detectable issues are found), false accepted matches, abstentions and unresolved residuals. Score legitimate timing/splits separately from errors. Compare groups as sets and partial allocations as amounts; do not rely on report row order. Cases unresolvable from visible evidence must expect investigation, not oracle certainty.

**Isolation tests:** run the matcher with only observed files; omit private files entirely and change private labels while holding observations constant. Output must not change. Ordinary reports and initial lesson prompts must not include answers/private IDs. Evaluator may access private truth only after engine output is complete.

**Integration and round-trip tests:** CSV → typed records → XLSX → typed records preserves exact money/IDs/dates and links. Verify numeric totals independently of workbook formula caches. Test repeated amounts, repeated legitimate invoices, empty inputs, quoted commas, unicode descriptions, blank keys, later clearing and prior-period outstanding carry-forward. An empty dataset does not automatically prove a zero-balance statement complete.

**Property tests later:** generate balanced journals, equivalent line orderings and random normalization inputs; verify conservation, rejection behavior and round trips. Preserve failing examples. Keep fixed seeds/scenarios alongside randomized tests so a human can understand failures. [Hypothesis explains useful properties and round trips](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html).

### Design traps and misleading implementations

| Trap | Required design response |
|---|---|
| Debits treated as expenses and credits as income | Use account type and economic substance; show both sides |
| Cash deposits automatically treated as revenue | Identify contributions, borrowings, receivable collections and refunds |
| Equal debits/credits treated as proof of correctness | Test classification, timing, evidence and completeness independently |
| Balanced books or matched bank rows treated as proof of accurate statements | Misclassification, missing noncash accruals and duplicate complete entries can remain balanced |
| Outstanding checks/deposits reposted | Teach timing items; inspect correct original posting and later settlement |
| Matching confidence confused with accounting certainty | Separate candidate ranking, evidence sufficiency, classification and review |
| All unmatched records called errors | Carry timing items, allow missing evidence, validate statement coverage |
| Same amounts/descriptions merged or dropped | Preserve multiplicity and references; constrain allocation ownership |
| Bank-side debit signs copied to company journal sides | Normalize to business cash perspective explicitly |
| Raw imported books silently repaired | Preserve raw files and rejected rows; approved corrections are new journal entries |
| Ground truth generated/evaluated solely with the same engine | Use independent fixtures and conservation checks; withhold labels from matcher |
| Scenario IDs leak error types into features | Use neutral observable IDs and private linkage tables |
| Float tolerances conceal cents discrepancies | Integer posted money; documented rounding for fractional calculations; differences stay explicit |
| XLSX formulas treated as calculated results | Compute authoritative values in Python; display optional manual formulas separately |
| Profit equated with cash flow | Teach accruals and working capital; build a reconciled cash-flow bridge later |
| Dates flattened into one date | Preserve recognition, posting and settlement dates; explicit cutoff policies |
| Corrections overwrite history or always use adjusting entries | Distinguish ordinary missing postings, corrections, month-end adjustments and reversals |
| AI invents tax, depreciation or recognition policy | State assumptions, source jurisdiction/year-specific rules later, flag incomplete evidence |
| Text templates drift from numeric results | Render account and statement effects from the shared assessment; test explanations against postings |
| Spreadsheet text becomes executable formula content | Export imported free-text as text; handle leading formula characters explicitly in CSV/XLSX exports |

## C. First small implementation task after approval

Build **a five-entry accounting kernel**, without random generation, reconciliation or a learning UI yet. Use six accounts: Checking, Owner capital, Service revenue, Rent expense, Office expense, and Owner drawings. Opening state is zero; owner funding is an ordinary contribution, not a second hidden opening balance.

| Entry | Economic event | Debit | Credit |
|---|---|---|---|
| J001 | Owner contributes $5,000 | Checking $5,000 | Owner capital $5,000 |
| J002 | Earn and receive $800 for completed services | Checking $800 | Service revenue $800 |
| J003 | Pay $600 rent for this period | Rent expense $600 | Checking $600 |
| J004 | Pay $75 for office items consumed this period | Office expense $75 | Checking $75 |
| J005 | Owner withdraws $200 for personal use | Owner drawings $200 | Checking $200 |

Deliver a minimal package, readable account/journal CSVs, entry validation, a derived ledger and trial balance, a plain-language walkthrough and meaningful pytest cases. XLSX follows in Milestone 3 so the first task stays small.

Acceptance: Checking $4,925 debit; Rent $600 debit; Office $75 debit; Drawings $200 debit; Capital $5,000 credit; Revenue $800 credit. Trial balance totals both equal $5,800. Profit is $125; ending equity is $4,925 after drawings; assets equal equity with no liabilities in this example. A deliberately unbalanced entry and an unknown account must fail validation. Expected totals must be explicit test constants, not derived by the production reporter. No implementation starts before the scope decisions below are resolved.

## D. Accounting concepts to review alongside that task

1. **Accounting equation:** assets = liabilities + owner's equity. Assets are resources, liabilities are obligations, and equity is the owner's residual interest.
2. **Double entry:** each entry records both sides of an economic event; totals balance even when more than two accounts are involved.
3. **Normal balances:** the usual debit/credit side for each account type; opposite-side entries can reduce a balance.
4. **Journal → ledger → trial balance:** chronological entries, account-by-account movements, then ending balance checks.
5. **Revenue, expenses and profit:** distinguish service earnings from funding; profit is revenue minus expenses for the period.
6. **Owner contributions and drawings:** equity movements; personal withdrawals are not expenses.
7. **Cash versus accrual timing:** the first tiny examples coincide with cash movements, but that is a simplification. The next lesson separates invoicing from collection.
8. **Evidence and scope:** “office expense” is justified here because items were consumed; a larger purchase with future benefit may require different treatment.

Suggested first reading: [OpenStax on the accounting cycle](https://openstax.org/books/principles-financial-accounting/pages/3-3-define-and-describe-the-initial-steps-in-the-accounting-cycle). Use the worked entries above to draw each account's two-sided ledger manually before comparing software output.

## E. Questions before implementation

1. **Business:** Is Cedar Desk Services suitable, or would you prefer another fictional business? A service business keeps inventory complexity out of the first lessons.
2. **Accounting basis and locale:** Approve USD and simplified accrual accounting? Which country/reporting context and entity type should guide terminology and eventual tax work? Tax can stay unspecified until its milestone.
3. **Learning workflow:** Prefer a terminal prompt with answer-before-reveal, or worksheet exercises with a separate answer report? Recommendation: terminal prompts plus inspection workbooks.
4. **Teaching depth:** Should each early entry include a detailed debit/credit walkthrough, or concise explanations with optional expansion? Recommendation: detailed initially.
5. **First implementation scope:** Approve the five-entry kernel as Milestone 2, then CSV/XLSX round trips, before random data and reconciliation?

Default proposed decisions, subject to your approval: service business; USD; simplified accrual; one checking account; terminal plus workbook; detailed early explanations; hand-checked kernel first. Implementation should confirm the available Python/runtime tooling locally and lock a tested dependency set. No application code, installs, workbook generation, or tax policy has been added in Milestone 1.
