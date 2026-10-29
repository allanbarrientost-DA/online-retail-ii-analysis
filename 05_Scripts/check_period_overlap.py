
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_combined.csv"
)


def main():
    print("Loading consolidated dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        parse_dates=["invoice_date"],
        dtype={
            "invoice": "string",
            "stock_code": "string",
        },
    )

    print("\nDate range by source period")
    print("=" * 65)

    period_summary = (
        df.groupby("source_period")
        .agg(
            rows=("invoice", "size"),
            first_date=("invoice_date", "min"),
            last_date=("invoice_date", "max"),
        )
        .reset_index()
    )

    print(period_summary.to_string(index=False))

    # Inspect dates that appear in both source periods.
    overlap_start = pd.Timestamp("2010-12-01")
    overlap_end = pd.Timestamp("2010-12-09 23:59:59")

    overlap = df[
        df["invoice_date"].between(
            overlap_start,
            overlap_end,
        )
    ].copy()

    print("\nRecords from December 1–9, 2010")
    print("=" * 65)

    print(
        overlap.groupby("source_period")
        .agg(
            rows=("invoice", "size"),
            unique_invoices=("invoice", "nunique"),
        )
        .to_string()
    )

    # Compare original transaction fields across the two periods.
    
    # Compare original transaction fields across the two periods.
    comparison_columns = [
        "invoice",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "unit_price",
        "customer_id",
        "country",
    ]

    first_period = overlap[
        overlap["source_period"] == "2009-2010"
    ][comparison_columns].copy()

    second_period = overlap[
        overlap["source_period"] == "2010-2011"
    ][comparison_columns].copy()

    # Convert values to a consistent format and represent
    # missing values explicitly before comparing rows.
    missing_marker = "<MISSING_VALUE>"

    for frame in [first_period, second_period]:
        for column in comparison_columns:
            frame[column] = (
                frame[column]
                .astype("string")
                .fillna(missing_marker)
            )

    # Count occurrences of each distinct transaction row.
    first_counts = (
        first_period
        .groupby(
            comparison_columns,
            dropna=False,
        )
        .size()
        .reset_index(name="count_first")
    )

    second_counts = (
        second_period
        .groupby(
            comparison_columns,
            dropna=False,
        )
        .size()
        .reset_index(name="count_second")
    )

    # Find transaction rows present in both source periods.
    matches = first_counts.merge(
        second_counts,
        on=comparison_columns,
        how="inner",
    )

    # Count matching occurrences without overcounting
    # repeated rows within either period.
    shared_occurrences = int(
        matches[
            ["count_first", "count_second"]
        ].min(axis=1).sum()
    )

    print(
        "\nMatching transaction rows across periods: "
        f"{shared_occurrences:,}"
    )

if __name__ == "__main__":
    main()
