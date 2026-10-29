
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_DATA_DIR = PROJECT_DIR / "01_Original_Data"
PROCESSED_DATA_DIR = PROJECT_DIR / "02_Processed_Data"


SHEET_PERIODS = {
    "Year 2009-2010": "2009-2010",
    "Year 2010-2011": "2010-2011",
}


def find_excel_file():
    """Locate the original Excel workbook."""

    files = list(
        ORIGINAL_DATA_DIR.rglob("online_retail_II.xlsx")
    )

    if len(files) != 1:
        raise FileNotFoundError(
            f"Expected one Excel workbook, found {len(files)}."
        )

    return files[0]


def load_worksheet(workbook, sheet_name, period):
    """Load one worksheet and standardize its column names."""

    df = pd.read_excel(
        workbook,
        sheet_name=sheet_name,
        dtype={
            "Invoice": "string",
            "StockCode": "string",
        },
    )

    df = df.rename(
        columns={
            "Invoice": "invoice",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "Price": "unit_price",
            "Customer ID": "customer_id",
            "Country": "country",
        }
    )

    # Keep customer IDs as text while preserving missing values.
    customer_ids = pd.to_numeric(
        df["customer_id"], errors="coerce"
    ).astype("Int64")

    df["customer_id"] = customer_ids.astype("string")

    # Record the source period for later comparisons.
    df["source_period"] = period

    return df


def main():
    file_path = find_excel_file()
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    frames = []

    with pd.ExcelFile(file_path) as workbook:
        for sheet_name, period in SHEET_PERIODS.items():
            print(f"Loading worksheet: {sheet_name}")

            df = load_worksheet(
                workbook,
                sheet_name,
                period,
            )

            print(f"Rows loaded: {len(df):,}")
            frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    del frames

    # Calculate the value of each transaction line.
    # This is not yet a cleaned net-sales measure.
    combined["line_amount"] = (
        combined["quantity"] * combined["unit_price"]
    )

    output_file = (
        PROCESSED_DATA_DIR / "online_retail_combined.csv"
    )

    combined.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )

    print("\n" + "=" * 60)
    print("DATASET CONSOLIDATION SUMMARY")
    print("=" * 60)

    print(f"Total rows: {len(combined):,}")
    print(f"Total columns: {len(combined.columns)}")

    print("\nRows by source period:")
    print(combined["source_period"].value_counts().to_string())

    print("\nMissing customer IDs:")
    print(f"{combined['customer_id'].isna().sum():,}")

    print("\nMissing descriptions:")
    print(f"{combined['description'].isna().sum():,}")

    print("\nTotal line amount across all records:")
    print(f"{combined['line_amount'].sum():,.2f}")

    print("\nColumn names:")
    print(", ".join(combined.columns))

    print(f"\nConsolidated dataset saved to:\n{output_file}")
    print("\nDataset preparation completed.")


if __name__ == "__main__":
    main()
