
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = (
    PROJECT_DIR
    / "02_Processed_Data"
    / "online_retail_combined.csv"
)


def main():
    print("Loading consolidated dataset...")

    df = pd.read_csv(
        DATA_FILE,
        low_memory=False,
        dtype={
            "invoice": "string",
            "stock_code": "string",
            "customer_id": "string",
        },
    )

    print("\n" + "=" * 60)
    print("CONSOLIDATED DATASET VALIDATION")
    print("=" * 60)

    # 1. Check dataset structure.
    print("\n1. DATASET STRUCTURE")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Duplicate rows: {df.duplicated().sum():,}")

    # 2. Check source periods.
    print("\n2. SOURCE PERIODS")
    print(df["source_period"].value_counts().to_string())

    # 3. Check missing values.
    print("\n3. MISSING VALUES")
    print(df.isna().sum().to_string())

    # 4. Check transaction values.
    print("\n4. TRANSACTION CHECKS")
    print(f"Negative quantities: {(df['quantity'] < 0).sum():,}")
    print(f"Zero prices: {(df['unit_price'] == 0).sum():,}")
    print(f"Negative prices: {(df['unit_price'] < 0).sum():,}")

    invoice_ids = df["invoice"].str.strip()
    cancellations = invoice_ids.str.startswith("C", na=False)

    print(
        "Invoice IDs starting with C: "
        f"{cancellations.sum():,}"
    )

    # 5. Check dates.
    print("\n5. DATE CHECKS")
    dates = pd.to_datetime(df["invoice_date"], errors="coerce")

    print(f"Invalid dates: {dates.isna().sum():,}")
    print(f"Earliest date: {dates.min()}")
    print(f"Latest date: {dates.max()}")

    # 6. Verify line_amount.
    print("\n6. LINE AMOUNT VALIDATION")
    expected_amount = df["quantity"] * df["unit_price"]

    matches = np.isclose(
        df["line_amount"].to_numpy(dtype=float),
        expected_amount.to_numpy(dtype=float),
        equal_nan=True,
    )

    print(f"Rows with correct line_amount: {matches.sum():,}")
    print(f"Rows with mismatched line_amount: {(~matches).sum():,}")

    print("\nValidation completed.")


if __name__ == "__main__":
    main()
