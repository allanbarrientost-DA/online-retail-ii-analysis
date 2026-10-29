
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_flagged.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)


def main():
    print("Loading flagged dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        parse_dates=["invoice_date"],
        dtype={
            "invoice": "string",
            "stock_code": "string",
            "customer_id": "string",
            "source_period": "string",
        },
    )

    original_rows = len(df)

    overlap_start = pd.Timestamp("2010-12-01")
    overlap_end = pd.Timestamp("2010-12-09 23:59:59")

    is_overlapping_period = (
        df["source_period"].eq("2009-2010")
        & df["invoice_date"].between(
            overlap_start,
            overlap_end,
        )
    )

    removed_rows = int(is_overlapping_period.sum())

    analysis_df = df.loc[~is_overlapping_period].copy()

    analysis_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nOVERLAP HANDLING SUMMARY")
    print("=" * 60)
    print(f"Original rows: {original_rows:,}")
    print(f"Rows excluded: {removed_rows:,}")
    print(f"Rows retained: {len(analysis_df):,}")

    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print("\nOriginal dataset remains unchanged.")


if __name__ == "__main__":
    main()
