
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"
RESULTS_DIR = PROJECT_DIR / "03_Results"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR / "large_cancellation_diagnostics.csv"
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

    # Select cancellation lines with quantities of 1,000 or more.
    cancellations = df[
        df["invoice"].str.startswith("C", na=False)
        & (df["quantity"] < 0)
        & (df["quantity"].abs() >= 1000)
    ].copy()

    # Create an absolute quantity for matching cancellation lines
    # with records that have positive quantities.
    cancellations["match_quantity"] = (
        cancellations["quantity"].abs()
    )

    positive = df[
        df["quantity"] > 0
    ].copy()

    positive["match_quantity"] = positive["quantity"]

    # Define the fields used to identify candidate matches.
    match_keys = [
        "stock_code",
        "customer_id",
        "unit_price",
        "match_quantity",
    ]

    # Keep unique combinations of positive records.
    positive_keys = positive[match_keys].drop_duplicates()

    # Identify whether each cancellation has a matching
    # positive record with the same product, customer,
    # unit price, and absolute quantity.
    cancellations = cancellations.merge(
        positive_keys.assign(
            has_matching_positive_record=True
        ),
        on=match_keys,
        how="left",
    )

    cancellations["has_matching_positive_record"] = (
        cancellations["has_matching_positive_record"]
        .fillna(False)
        .astype(bool)
    )

    # Display summary statistics.
    matching_flags = cancellations[
        "has_matching_positive_record"
    ]

    print("\nLARGE CANCELLATION SUMMARY")
    print("=" * 80)

    print(
        f"Cancellation lines found: {len(cancellations):,}"
    )

    print(
        "Lines with a matching positive record: "
        f"{matching_flags.sum():,}"
    )

    print(
        "Lines without a matching positive record: "
        f"{(~matching_flags).sum():,}"
    )

    # Display the largest cancellation quantities first.
    columns_to_show = [
        "invoice",
        "invoice_date",
        "stock_code",
        "description",
        "quantity",
        "unit_price",
        "line_amount",
        "customer_id",
        "has_matching_positive_record",
    ]

    cancellations = cancellations.sort_values(
        "quantity"
    )

    print("\nCANCELLATIONS ORDERED BY QUANTITY")
    print("=" * 100)

    print(
        cancellations[columns_to_show]
        .to_string(index=False)
    )

    # Save the diagnostic report.
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    cancellations[columns_to_show].to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nReport saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
