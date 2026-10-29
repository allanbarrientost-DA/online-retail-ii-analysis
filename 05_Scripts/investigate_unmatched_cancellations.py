
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"
RESULTS_DIR = PROJECT_DIR / "03_Results"

INPUT_FILE = (
    PROCESSED_DATA_DIR / "online_retail_analysis.csv"
)

OUTPUT_FILE = (
    RESULTS_DIR / "unmatched_cancellation_details.csv"
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

    # Select large cancellation lines.
    cancellations = df[
        df["invoice"].str.startswith("C", na=False)
        & (df["quantity"] <= -1000)
    ].copy()

    # Find positive records matching product, customer,
    # unit price, and absolute quantity.
    cancellations["match_quantity"] = (
        cancellations["quantity"].abs()
    )

    positive = df[df["quantity"] > 0].copy()
    positive["match_quantity"] = positive["quantity"]

    match_keys = [
        "stock_code",
        "customer_id",
        "unit_price",
        "match_quantity",
    ]

    positive_keys = positive[match_keys].drop_duplicates()

    cancellations = cancellations.merge(
        positive_keys.assign(exact_match=True),
        on=match_keys,
        how="left",
    )

    cancellations["exact_match"] = (
        cancellations["exact_match"]
        .fillna(False)
        .astype(bool)
    )

    unmatched = cancellations[
        ~cancellations["exact_match"]
    ].copy()

    print("\nUNMATCHED LARGE CANCELLATIONS")
    print("=" * 90)
    print(f"Records to investigate: {len(unmatched):,}")

    # Search for any positive record for the same product
    # and customer, regardless of quantity or unit price.
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

    for _, cancellation in unmatched.iterrows():
        print("\n" + "-" * 90)
        print(
            f"Cancellation invoice: {cancellation['invoice']}"
        )
        print(
            f"Product code: {cancellation['stock_code']}"
        )
        print(
            f"Customer ID: {cancellation['customer_id']}"
        )

        same_product_customer = df[
            (df["stock_code"] == cancellation["stock_code"])
            & (
                df["customer_id"]
                == cancellation["customer_id"]
            )
            & (df["quantity"] > 0)
        ].copy()

        print(
            "Positive records for the same product and customer: "
            f"{len(same_product_customer):,}"
        )

        if not same_product_customer.empty:
            print(
                same_product_customer[columns_to_show]
                .sort_values("invoice_date")
                .to_string(index=False)
            )
        else:
            print("No positive records found for this product and customer.")

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    unmatched[columns_to_show].to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nReport saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
