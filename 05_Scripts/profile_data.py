
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_DATA_DIR = PROJECT_DIR / "01_Original_Data"


def find_excel_file():
    """Locate the original Excel workbook."""

    files = list(ORIGINAL_DATA_DIR.rglob("online_retail_II.xlsx"))

    if len(files) != 1:
        raise FileNotFoundError(
            f"Expected one Excel workbook, found {len(files)}."
        )

    return files[0]


def profile_worksheet(file_path, sheet_name):
    """Inspect data quality without changing the source data."""

    print("\n" + "=" * 65)
    print(f"DATA QUALITY PROFILE: {sheet_name}")
    print("=" * 65)

    df = pd.read_excel(file_path, sheet_name=sheet_name)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nCOLUMN DATA TYPES")
    print(df.dtypes.to_string())

    print("\nMISSING VALUES")
    missing = df.isna().sum()
    missing_report = pd.DataFrame({
        "Missing_Count": missing,
        "Missing_Percentage": (missing / len(df) * 100).round(2)
    })
    print(missing_report.to_string())

    print("\nDUPLICATE ROWS")
    print(f"Fully duplicated rows: {df.duplicated().sum():,}")

    print("\nQUANTITY AND PRICE CHECKS")
    print(f"Negative quantities: {(df['Quantity'] < 0).sum():,}")
    print(f"Zero quantities: {(df['Quantity'] == 0).sum():,}")
    print(f"Negative prices: {(df['Price'] < 0).sum():,}")
    print(f"Zero prices: {(df['Price'] == 0).sum():,}")

    print("\nINVOICE CHECKS")
    invoice_ids = df["Invoice"].astype("string").str.strip()
    cancellation_mask = invoice_ids.str.startswith("C", na=False)
    print(f"Invoice IDs starting with C: {cancellation_mask.sum():,}")

    print("\nCUSTOMER CHECK")
    print(f"Rows without Customer ID: {df['Customer ID'].isna().sum():,}")

    del df


def main():
    file_path = find_excel_file()

    print(f"Source workbook: {file_path.name}")

    workbook = pd.ExcelFile(file_path)

    try:
        for sheet_name in workbook.sheet_names:
            profile_worksheet(file_path, sheet_name)
    finally:
        workbook.close()

    print("\nInitial data quality assessment completed.")


if __name__ == "__main__":
    main()
