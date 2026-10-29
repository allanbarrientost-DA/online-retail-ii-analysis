
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"
RESULTS_DIR = PROJECT_DIR / "03_Results"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR / "monthly_sales_overview.csv"
)


def main():
    print("Loading retail dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        parse_dates=["invoice_date"],
    )

    print(f"Rows loaded: {len(df):,}")

    # Create a monthly period for grouping.
    df["month"] = (
        df["invoice_date"]
        .dt.to_period("M")
        .astype(str)
    )

    # Calculate a preliminary monthly overview.
    monthly = (
        df.groupby("month")
        .agg(
            transaction_lines=("invoice", "size"),
            unique_invoices=("invoice", "nunique"),
            units_sold=("quantity", "sum"),
            line_amount_total=("line_amount", "sum"),
        )
        .reset_index()
    )

    print("\nMONTHLY OVERVIEW")
    print("=" * 70)
    print(monthly.to_string(index=False))

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    monthly.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print(
        "\nNote: line_amount_total is preliminary "
        "and is not yet a validated net-sales measure."
    )


if __name__ == "__main__":
    main()
