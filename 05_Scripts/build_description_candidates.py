
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_DATA_DIR = PROJECT_DIR / "01_Original_Data"
DOCUMENTATION_DIR = PROJECT_DIR / "04_Documentation"


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


def main():
    file_path = find_excel_file()
    DOCUMENTATION_DIR.mkdir(parents=True, exist_ok=True)

    frames = []

    # Read product codes and descriptions from both periods.
    with pd.ExcelFile(file_path) as workbook:
        for sheet_name in workbook.sheet_names:
            df = pd.read_excel(
                workbook,
                sheet_name=sheet_name,
                dtype={
                    "StockCode": "string",
                    "Description": "string",
                },
                usecols=["StockCode", "Description"],
            )

            frames.append(df)

    products = pd.concat(frames, ignore_index=True)
    del frames

    # Trim whitespace for analysis without changing the source workbook.
    products["Description"] = products["Description"].str.strip()

    missing_mask = (
        products["Description"].isna()
        | products["Description"].eq("")
    )

    missing_counts = (
        products.loc[missing_mask]
        .groupby("StockCode")
        .size()
        .rename("Missing_Description_Rows")
        .reset_index()
    )

    valid_descriptions = products.loc[
        products["StockCode"].notna()
        & products["Description"].notna()
        & products["Description"].ne("")
    ]

    # Count how often each description appears for each product code.
    candidates = (
        valid_descriptions
        .groupby(["StockCode", "Description"])
        .size()
        .rename("Description_Frequency")
        .reset_index()
    )

    # Keep candidate descriptions only for codes with missing descriptions.
    report = candidates.merge(
        missing_counts,
        on="StockCode",
        how="inner",
    )

    report = report.sort_values(
        ["StockCode", "Description_Frequency"],
        ascending=[True, False],
    )

    output_file = (
        DOCUMENTATION_DIR / "description_candidates.csv"
    )

    report.to_csv(output_file, index=False, encoding="utf-8-sig")

    codes_with_candidates = report["StockCode"].nunique()
    total_missing_codes = missing_counts["StockCode"].nunique()

    print("=" * 65)
    print("DESCRIPTION CANDIDATE REPORT")
    print("=" * 65)
    print(f"Rows with missing descriptions: {missing_mask.sum():,}")
    print(f"Distinct product codes with missing descriptions: "
          f"{total_missing_codes:,}")
    print(f"Codes with at least one candidate description: "
          f"{codes_with_candidates:,}")
    print(f"Codes without a candidate description: "
          f"{total_missing_codes - codes_with_candidates:,}")
    print(f"\nReport saved to:\n{output_file}")
    print("\nFirst 20 candidate rows:")
    print(report.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
