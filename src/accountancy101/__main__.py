"""Run the fixed five-entry example and write its four CSV files."""

import argparse
from pathlib import Path

from .csv_output import export_csv
from .sample import ACCOUNTS, ENTRIES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/milestone2"))
    args = parser.parse_args()
    export_csv(args.output, ACCOUNTS, ENTRIES)
    print(f"Wrote accounts, journal, ledger and trial balance CSVs to {args.output.resolve()}")


if __name__ == "__main__":
    main()
