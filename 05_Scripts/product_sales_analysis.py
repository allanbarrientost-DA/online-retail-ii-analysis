
"""
Analyze product activity, positive line amounts, and negative amounts
for the Online Retail II portfolio project.
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = (
    PROJECT_ROOT
    / "02_Processed_Data"
    / "online_retail_analysis.csv"
)
RESULTS_DIR = PROJECT_ROOT / "03_Results"
OUTPUT_FILE = RESULTS_DIR / "product_sales_overview.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Load only the required fields.
df = pd.read_csv(
    DATA_FILE,
    usecols=[
        "invoice",
        "stock_code",
        "description",
        "quantity",
        "line_amount",
    ],
    dtype={
        "invoice": "string",
        "stock_code": "string",
        "description": "string",
    },
)

# Validate the input data.
required_columns = {
    "invoice",
    "stock_code",
    "description",
    "quantity",
    "line_amount",
}

if not required_columns.issubset(df.columns):
    raise ValueError("The input dataset is missing required columns.")

if df["stock_code"].isna().any():
    raise ValueError("Missing stock codes were found.")

# Separate positive and negative line amounts.
df["positive_line_amount"] = df["line_amount"].where(
    df["line_amount"] > 0, 0
)
df["negative_line_amount"] = df["line_amount"].where(
    df["line_amount"] < 0, 0
)

# Identify cancellation invoice lines.
df["is_cancellation"] = (
    df["invoice"].str.startswith("C", na=False).astype(int)
)

# Select the most frequent non-missing description per stock code.
def most_common_description(series):
    descriptions = series.dropna().str.strip()
    descriptions = descriptions[descriptions != ""]

    if descriptions.empty:
        return "Unknown description"

    return descriptions.value_counts().index[0]


# Aggregate product-level metrics.
product_summary = (
    df.groupby("stock_code", as_index=False)
    .agg(
        description=("description", most_common_description),
        description_variants=("description", "nunique"),
        transaction_lines=("invoice", "size"),
        unique_invoices=("invoice", "nunique"),
        total_quantity=("quantity", "sum"),
        positive_line_amount=("positive_line_amount", "sum"),
        negative_line_amount=("negative_line_amount", "sum"),
        net_line_amount=("line_amount", "sum"),
        cancellation_lines=("is_cancellation", "sum"),
    )
)

# Calculate the share of transaction lines.
total_lines = product_summary["transaction_lines"].sum()
product_summary["transaction_line_share_pct"] = (
    product_summary["transaction_lines"] / total_lines * 100
)

# Export the complete product summary.
product_summary = product_summary.sort_values(
    "positive_line_amount",
    ascending=False,
)

product_summary.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8",
)

# Display dataset overview.
print("Product analysis completed successfully.")
print(f"Dataset rows: {len(df):,}")
print(f"Unique stock codes: {df['stock_code'].nunique():,}")
print(f"Product summary saved to: {OUTPUT_FILE}")

print("\n=== TOP 10 PRODUCTS BY TRANSACTION LINES ===")
print(
    product_summary.nlargest(10, "transaction_lines")[
        [
            "stock_code",
            "description",
            "transaction_lines",
            "unique_invoices",
        ]
    ].to_string(index=False)
)

print("\n=== TOP 10 PRODUCTS BY POSITIVE LINE AMOUNT ===")
print(
    product_summary.nlargest(10, "positive_line_amount")[
        [
            "stock_code",
            "description",
            "positive_line_amount",
            "negative_line_amount",
            "net_line_amount",
        ]
    ].to_string(index=False)
)

print("\n=== TOP 10 PRODUCTS BY NEGATIVE AMOUNT MAGNITUDE ===")
negative_products = product_summary.assign(
    negative_amount_magnitude=product_summary[
        "negative_line_amount"
    ].abs()
)

print(
    negative_products.nlargest(10, "negative_amount_magnitude")[
        [
            "stock_code",
            "description",
            "negative_amount_magnitude",
            "cancellation_lines",
            "net_line_amount",
        ]
    ].to_string(index=False)
)

print("\n=== DATA QUALITY CHECK ===")
print(
    "Rows with missing descriptions:",
    df["description"].isna().sum(),
)
print(
    "Stock codes with multiple descriptions:",
    (product_summary["description_variants"] > 1).sum(),
)
