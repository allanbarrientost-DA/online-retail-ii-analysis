
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


def main():
    file_path = find_excel_file()

    all_data = []

    # Load both periods to compare product descriptions.
    for sheet_name in pd.ExcelFile(file_path).sheet_names:
        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
            dtype={
                "StockCode": "string",
                "Description": "string",
            },
            usecols=["StockCode", "Description"],
        )

        all_data.append(df)

    products = pd.concat(all_data, ignore_index=True)
    del all_data

    # Remove surrounding whitespace for comparison only.
    products["Description"] = (
        products["Description"].str.strip()
    )

    valid_descriptions = products.loc[
        products["Description"].notna()
        & products["Description"].ne("")
    ]

    # Count distinct descriptions associated with each product code.
    descriptions_per_code = (
        valid_descriptions
        .groupby("StockCode")["Description"]
        .nunique()
    )

    codes_with_descriptions = set(descriptions_per_code.index)

    missing_description_rows = products[
        products["Description"].isna()
        | products["Description"].eq("")
    ]

    missing_codes = missing_description_rows["StockCode"]

    recoverable_mask = missing_codes.isin(codes_with_descriptions)

    print("=" * 65)
    print("PRODUCT DESCRIPTION INVESTIGATION")
    print("=" * 65)

    print(
        "\nRows with missing descriptions:",
        f"{len(missing_description_rows):,}",
    )
    print(
        "Rows whose StockCode has a description elsewhere:",
        f"{recoverable_mask.sum():,}",
    )
    print(
        "Rows whose StockCode has no valid description elsewhere:",
        f"{(~recoverable_mask).sum():,}",
    )

    print("\nPRODUCT CODES WITH MULTIPLE DESCRIPTIONS")
    multiple_descriptions = descriptions_per_code[
        descriptions_per_code > 1
    ]

    print(
        "Number of codes with multiple descriptions:",
        f"{len(multiple_descriptions):,}",
    )

    if not multiple_descriptions.empty:
        example_codes = multiple_descriptions.index[:10]

        examples = valid_descriptions[
            valid_descriptions["StockCode"].isin(example_codes)
        ].drop_duplicates().sort_values("StockCode")

        print(examples.to_string(index=False))

    print("\nEXAMPLES OF MISSING DESCRIPTIONS WITH MATCHING CODES")

    examples_missing = missing_description_rows.loc[
        recoverable_mask
    ].head(10)

    if examples_missing.empty:
        print("No matching product codes found.")
    else:
        print(examples_missing.to_string(index=False))

        matching_examples = valid_descriptions[
            valid_descriptions["StockCode"].isin(
                examples_missing["StockCode"]
            )
        ].drop_duplicates().sort_values("StockCode")

        print("\nKnown descriptions for these codes:")
        print(matching_examples.to_string(index=False))

    print("\nProduct description investigation completed.")


if __name__ == "__main__":
    main()
