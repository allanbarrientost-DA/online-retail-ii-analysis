
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"
RESULTS_DIR = PROJECT_DIR / "03_Results"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR / "monthly_sales_components.csv"
)


def main():
    print("Loading analysis dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        parse_dates=["invoice_date"],
        dtype={
            "invoice": "string",
            "stock_code": "string",
        },
    )

    # Create monthly groups.
    df["month"] = (
        df["invoice_date"]
        .dt.to_period("M")
        .astype(str)
    )

    # Classify line amounts for descriptive analysis.
    df["positive_amount"] = df["line_amount"].where(
        df["line_amount"] > 0,
        0,
    )

    df["negative_amount"] = df["line_amount"].where(
        df["line_amount"] < 0,
        0,
    )

    df["zero_amount_lines"] = (
        df["line_amount"] == 0
    ).astype(int)

    monthly = (
        df.groupby("month")
        .agg(
            transaction_lines=("invoice", "size"),
            positive_amount_total=("positive_amount", "sum"),
            negative_amount_total=("negative_amount", "sum"),
            zero_amount_lines=("zero_amount_lines", "sum"),
            total_line_amount=("line_amount", "sum"),
        )
        .reset_index()
    )

    # Absolute value helps quantify the magnitude of negative amounts.
    monthly["negative_amount_magnitude"] = (
        monthly["negative_amount_total"].abs()
    )

    print("\nMONTHLY SALES COMPONENTS")
    print("=" * 95)
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
        "\nNote: positive amounts are not automatically "
        "confirmed sales, and negative amounts are not "
        "automatically confirmed returns."
    )


if __name__ == "__main__":
    main()
