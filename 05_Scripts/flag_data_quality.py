
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_combined.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_flagged.csv"
)


def main():
    print("Loading consolidated dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        dtype={
            "invoice": "string",
            "stock_code": "string",
            "customer_id": "string",
        },
    )

    print(f"Rows loaded: {len(df):,}")

    # Normalize invoice IDs for classification only.
    invoice_ids = df["invoice"].str.strip()

    # Create quality flags without removing records.
    df["is_cancellation"] = invoice_ids.str.startswith(
        "C", na=False
    )

    df["has_negative_quantity"] = df["quantity"] < 0
    df["has_zero_price"] = df["unit_price"] == 0
    df["has_negative_price"] = df["unit_price"] < 0

    df["has_missing_customer"] = df["customer_id"].isna()
    df["has_missing_description"] = (
        df["description"].isna()
        | df["description"].str.strip().eq("").fillna(False)
    )

    # Mark every row that belongs to an exact duplicate group.
    df["is_exact_duplicate"] = df.duplicated(
        keep=False
    )

    # Mark only repeated occurrences after the first.
    df["is_duplicate_after_first"] = df.duplicated(
        keep="first"
    )

    # Summarize flags before exporting.
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

    print("\n" + "=" * 60)
    print("DATA QUALITY FLAG SUMMARY")
    print("=" * 60)

    for column in flag_columns:
        count = int(df[column].sum())
        percentage = count / len(df) * 100

        print(
            f"{column}: {count:,} rows ({percentage:.2f}%)"
        )

    # Export all records, including those flagged for review.
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nTotal rows exported: {len(df):,}")
    print(f"Output file: {OUTPUT_FILE}")
    print("\nQuality flagging completed. No rows were removed.")


if __name__ == "__main__":
    main()
