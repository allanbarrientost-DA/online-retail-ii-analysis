
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
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

    # Investigate the invoice containing the largest negative amount.
    target_invoice = df[
        df["invoice"] == "C581484"
    ].copy()

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
        "source_period",
    ]

    print("\nTARGET INVOICE: C581484")
    print("=" * 100)

    if target_invoice.empty:
        print("Invoice not found.")
    else:
        print(
            target_invoice[columns_to_show]
            .to_string(index=False)
        )

    # Find all records for the same product code.
    target_product = df[
        df["stock_code"] == "23843"
    ].copy()

    print("\nPRODUCT CODE: 23843")
    print("=" * 100)
    print(f"Total records: {len(target_product):,}")
    print(
        "Positive-quantity records: "
        f"{(target_product['quantity'] > 0).sum():,}"
    )
    print(
        "Negative-quantity records: "
        f"{(target_product['quantity'] < 0).sum():,}"
    )
    print(
        "Total quantity: "
        f"{target_product['quantity'].sum():,.0f}"
    )
    print(
        "Total line amount: "
        f"{target_product['line_amount'].sum():,.2f}"
    )

    print("\nRECORDS FOR PRODUCT 23843")
    print("=" * 100)

    print(
        target_product[columns_to_show]
        .sort_values("invoice_date")
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
