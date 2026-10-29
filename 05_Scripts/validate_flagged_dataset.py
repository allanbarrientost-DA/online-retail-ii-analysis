
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_flagged.csv"
)


def main():
    print("Loading flagged dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
    )

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    flag_columns = [
        "is_cancellation",
        "has_negative_quantity",
        "has_zero_price",
        "has_negative_price",
        "has_missing_customer",
        "has_missing_description",
        "is_exact_duplicate",
        "is_duplicate_after_first",
    ]

    print("\nChecking flag columns...")

    missing_columns = [
        column
        for column in flag_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(f"Missing columns: {missing_columns}")
        return

    for column in flag_columns:
        count = int(df[column].sum())
        print(f"{column}: {count:,}")

    print("\nChecking duplicate flag consistency...")

    inconsistent_duplicates = (
        df["is_duplicate_after_first"]
        & ~df["is_exact_duplicate"]
    ).sum()

    print(
        "Repeated rows not marked as duplicate-group rows: "
        f"{int(inconsistent_duplicates):,}"
    )

    print("\nValidation completed.")


if __name__ == "__main__":
    main()
