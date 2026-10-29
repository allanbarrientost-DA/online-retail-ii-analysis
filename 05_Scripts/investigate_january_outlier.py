
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

    # Investigate the unusually large January cancellation.
    product_code = "23166"
    customer_code = "12346"

    product_records = df[
        (df["stock_code"] == product_code)
        & (df["customer_id"] == customer_code)
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
    ]

    product_records = product_records.sort_values(
        "invoice_date"
    )

    print("\nALL RECORDS FOR THIS PRODUCT AND CUSTOMER")
    print("=" * 100)
    print(
        product_records[columns_to_show]
        .to_string(index=False)
    )

    print("\nSUMMARY")
    print("=" * 100)
    print(f"Matching records: {len(product_records):,}")
    print(
        "Positive-quantity records: "
        f"{(product_records['quantity'] > 0).sum():,}"
    )
    print(
        "Negative-quantity records: "
        f"{(product_records['quantity'] < 0).sum():,}"
    )
    print(
        "Total quantity: "
        f"{product_records['quantity'].sum():,.0f}"
    )
    print(
        "Total line amount: "
        f"{product_records['line_amount'].sum():,.2f}"
    )


if __name__ == "__main__":
    main()
