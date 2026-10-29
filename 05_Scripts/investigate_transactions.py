
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_DATA_DIR = PROJECT_DIR / "01_Original_Data"


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


def investigate_worksheet(file_path, sheet_name):
    """Investigate unusual transaction records."""

    print("\n" + "=" * 70)
    print(f"TRANSACTION INVESTIGATION: {sheet_name}")
    print("=" * 70)

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        dtype={
            "Invoice": "string",
            "StockCode": "string",
            "Description": "string",
        },
    )

    # Standardize invoice IDs for inspection only.
    invoice_ids = df["Invoice"].str.strip()
    cancellation_mask = invoice_ids.str.startswith(
        "C", na=False
    )
    negative_quantity_mask = df["Quantity"] < 0

    print("\n1. CANCELLATIONS AND NEGATIVE QUANTITIES")
    print(
        "Invoices starting with C:",
        f"{cancellation_mask.sum():,}",
    )
    print(
        "Rows with negative quantities:",
        f"{negative_quantity_mask.sum():,}",
    )
    print(
        "Rows meeting both conditions:",
        f"{(cancellation_mask & negative_quantity_mask).sum():,}",
    )
    print(
        "Rows starting with C but without negative quantity:",
        f"{(cancellation_mask & ~negative_quantity_mask).sum():,}",
    )
    print(
        "Negative quantities without invoice ID starting with C:",
        f"{(~cancellation_mask & negative_quantity_mask).sum():,}",
    )

    print("\n2. EXAMPLES OF EXACT DUPLICATE ROWS")
    duplicate_mask = df.duplicated(keep=False)
    duplicate_examples = df.loc[duplicate_mask].head(10)
    print(
        f"Rows belonging to duplicate groups: "
        f"{duplicate_mask.sum():,}"
    )
    if duplicate_examples.empty:
        print("No duplicate examples found.")
    else:
        print(duplicate_examples.to_string(index=False))

    print("\n3. ZERO-PRICE RECORDS")
    zero_price = df.loc[df["Price"] == 0]
    print(f"Total rows with zero price: {len(zero_price):,}")
    if not zero_price.empty:
        print(
            zero_price[
                ["Invoice", "StockCode", "Description",
                 "Quantity", "Price", "Customer ID", "Country"]
            ].head(10).to_string(index=False)
        )

    print("\n4. NEGATIVE-PRICE RECORDS")
    negative_price = df.loc[df["Price"] < 0]
    print(f"Total rows with negative price: {len(negative_price):,}")
    if not negative_price.empty:
        print(
            negative_price[
                ["Invoice", "StockCode", "Description",
                 "Quantity", "Price", "Customer ID", "Country"]
            ].to_string(index=False)
        )

    print("\n5. MISSING PRODUCT DESCRIPTIONS")
    missing_description = df["Description"].isna()
    print(
        "Rows with missing descriptions:",
        f"{missing_description.sum():,}",
    )
    print(
        "Rows with missing descriptions but a StockCode present:",
        f"{(missing_description & df['StockCode'].notna()).sum():,}",
    )

    print("\nExamples:")
    print(
        df.loc[
            missing_description,
            ["StockCode", "Description", "Quantity", "Price"]
        ].head(10).to_string(index=False)
    )

    del df


def main():
    file_path = find_excel_file()
    workbook = pd.ExcelFile(file_path)

    try:
        for sheet_name in workbook.sheet_names:
            investigate_worksheet(file_path, sheet_name)
    finally:
        workbook.close()

    print("\nTransaction investigation completed.")


if __name__ == "__main__":
    main()
