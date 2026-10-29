
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"
RESULTS_DIR = PROJECT_DIR / "03_Results"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR / "negative_amount_diagnostics.csv"
)


def main():
    print("Loading analysis dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False,
        parse_dates=["invoice_date"],
        dtype={
            "invoice": "string",
            "source_period": "string",
        },
    )

    # Create monthly groups.
    df["month"] = (
        df["invoice_date"]
        .dt.to_period("M")
        .astype(str)
    )

    # Identify rows with negative line amounts.
    negative = df[df["line_amount"] < 0].copy()

    print(f"Total rows: {len(df):,}")
    print(f"Negative-amount rows: {len(negative):,}")

    print("\nNEGATIVE AMOUNT DIAGNOSTICS")
    print("=" * 85)

    monthly = (
        df.assign(
            is_negative_amount=df["line_amount"] < 0,
            is_c_invoice=df["is_cancellation"],
            is_negative_quantity=df["has_negative_quantity"],
        )
        .groupby("month")
        .agg(
            negative_amount_rows=(
                "is_negative_amount",
                "sum",
            ),
            negative_amount_total=(
                "line_amount",
                lambda values: values[values < 0].sum(),
            ),
            c_invoice_rows=("is_c_invoice", "sum"),
            negative_quantity_rows=(
                "is_negative_quantity",
                "sum",
            ),
        )
        .reset_index()
    )

    print(monthly.to_string(index=False))

    # Examine how negative-amount rows overlap with other flags.
    print("\nOVERLAP AMONG NEGATIVE-AMOUNT ROWS")
    print("=" * 85)

    print(
        "Negative-amount rows with C invoice: "
        f"{int(negative['is_cancellation'].sum()):,}"
    )

    print(
        "Negative-amount rows with negative quantity: "
        f"{int(negative['has_negative_quantity'].sum()):,}"
    )

    print(
        "Negative-amount rows with negative unit price: "
        f"{int(negative['has_negative_price'].sum()):,}"
    )

    print(
        "Negative-amount rows with zero unit price: "
        f"{int(negative['has_zero_price'].sum()):,}"
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

    print(f"\nOutput saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
