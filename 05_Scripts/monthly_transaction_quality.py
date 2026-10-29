
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"
RESULTS_DIR = PROJECT_DIR / "03_Results"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR / "monthly_transaction_quality.csv"
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
            "customer_id": "string",
        },
    )

    # Derive monthly and transaction-level indicators.
    df["month"] = df["invoice_date"].dt.to_period("M").astype(str)

    df["is_cancellation"] = (
        df["invoice"].str.startswith("C", na=False)
    )

    df["is_negative_quantity"] = df["quantity"] < 0
    df["is_positive_quantity"] = df["quantity"] > 0
    df["is_negative_price"] = df["unit_price"] < 0
    df["is_zero_price"] = df["unit_price"] == 0

    # Summarize line amounts and data-quality indicators by month.
    monthly = (
        df.groupby("month")
        .agg(
            transaction_lines=("invoice", "size"),
            unique_invoices=("invoice", "nunique"),
            positive_quantity_lines=("is_positive_quantity", "sum"),
            negative_quantity_lines=("is_negative_quantity", "sum"),
            cancellation_lines=("is_cancellation", "sum"),
            negative_price_lines=("is_negative_price", "sum"),
            zero_price_lines=("is_zero_price", "sum"),
            positive_line_amount=(
                "line_amount",
                lambda values: values[values > 0].sum(),
            ),
            negative_line_amount=(
                "line_amount",
                lambda values: values[values < 0].sum(),
            ),
            zero_line_amount_lines=(
                "line_amount",
                lambda values: (values == 0).sum(),
            ),
        )
        .reset_index()
    )

    monthly["total_line_amount"] = (
        monthly["positive_line_amount"]
        + monthly["negative_line_amount"]
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    monthly.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nMONTHLY TRANSACTION QUALITY")
    print("=" * 100)
    print(monthly.to_string(index=False))

    print(f"\nReport saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
