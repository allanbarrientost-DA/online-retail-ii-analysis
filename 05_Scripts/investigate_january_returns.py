
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"
RESULTS_DIR = PROJECT_DIR / "03_Results"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR / "january_2011_negative_lines.csv"
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

    # Select negative-amount records from January 2011.
    january = df[
        (df["invoice_date"] >= "2011-01-01")
        & (df["invoice_date"] < "2011-02-01")
        & (df["line_amount"] < 0)
    ].copy()

    print(
        "\nNegative-amount rows in January 2011: "
        f"{len(january):,}"
    )

    print(
        "Total negative amount: "
        f"{january['line_amount'].sum():,.2f}"
    )

    columns_to_show = [
        "invoice",
        "invoice_date",
        "stock_code",
        "description",
        "quantity",
        "unit_price",
        "line_amount",
        "customer_id",
        "country",
    ]

    # Show the largest negative amounts first.
    largest = january.sort_values("line_amount")

    print("\n20 LARGEST NEGATIVE LINE AMOUNTS")
    print("=" * 100)
    print(
        largest[columns_to_show]
        .head(20)
        .to_string(index=False)
    )

    # Summarize negative amounts by invoice.
    invoice_summary = (
        january.groupby("invoice")
        .agg(
            line_count=("line_amount", "size"),
            invoice_negative_amount=("line_amount", "sum"),
            first_date=("invoice_date", "min"),
        )
        .sort_values("invoice_negative_amount")
        .reset_index()
    )

    print("\n10 INVOICES WITH THE LARGEST NEGATIVE TOTALS")
    print("=" * 100)
    print(
        invoice_summary.head(10).to_string(index=False)
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    largest[columns_to_show].to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nDetailed records saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
