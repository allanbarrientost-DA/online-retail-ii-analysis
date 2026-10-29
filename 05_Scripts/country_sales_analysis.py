
"""
Analyze transaction activity and line amounts by country
for the Online Retail II portfolio project.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "02_Processed_Data" / "online_retail_analysis.csv"
RESULTS_DIR = PROJECT_ROOT / "03_Results"
CHARTS_DIR = RESULTS_DIR / "Graficas"
OUTPUT_FILE = RESULTS_DIR / "country_sales_overview.csv"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Load only the fields required for this analysis.
df = pd.read_csv(
    DATA_FILE,
    usecols=["country", "invoice", "quantity", "unit_price", "line_amount"],
    dtype={"invoice": "string", "country": "string"},
)

# Validate the required fields.
required_columns = {
    "country", "invoice", "quantity", "unit_price", "line_amount"
}
if not required_columns.issubset(df.columns):
    raise ValueError("The input dataset is missing required columns.")

if df["country"].isna().any():
    raise ValueError("Missing country values were found.")

# Separate positive, negative, and zero line amounts.
df["positive_line_amount"] = df["line_amount"].where(
    df["line_amount"] > 0, 0
)
df["negative_line_amount"] = df["line_amount"].where(
    df["line_amount"] < 0, 0
)
df["zero_amount_line"] = (df["line_amount"] == 0).astype(int)

# Identify cancellation invoice lines.
df["is_cancellation"] = (
    df["invoice"].str.startswith("C", na=False).astype(int)
)

# Aggregate transaction and amount metrics by country.
country_summary = (
    df.groupby("country", as_index=False)
    .agg(
        transaction_lines=("invoice", "size"),
        unique_invoices=("invoice", "nunique"),
        total_quantity=("quantity", "sum"),
        positive_line_amount=("positive_line_amount", "sum"),
        negative_line_amount=("negative_line_amount", "sum"),
        net_line_amount=("line_amount", "sum"),
        zero_amount_lines=("zero_amount_line", "sum"),
        cancellation_lines=("is_cancellation", "sum"),
    )
)

# Add each country's share of all transaction lines.
total_lines = country_summary["transaction_lines"].sum()
country_summary["transaction_line_share_pct"] = (
    country_summary["transaction_lines"] / total_lines * 100
)

# Sort and export the complete country-level table.
country_summary = country_summary.sort_values(
    "positive_line_amount", ascending=False
)
country_summary.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

# Select the top 10 countries by transaction-line count.
top_lines = country_summary.nlargest(10, "transaction_lines")
top_lines = top_lines.sort_values("transaction_lines")

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(top_lines["country"], top_lines["transaction_lines"])
ax.set_title("Top 10 Countries by Transaction Lines")
ax.set_xlabel("Number of Transaction Lines")
ax.set_ylabel("Country")
ax.grid(axis="x", linestyle="--", alpha=0.3)
fig.tight_layout()
fig.savefig(
    CHARTS_DIR / "top_countries_by_transaction_lines.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close(fig)

# Select the top 10 countries by positive line amount.
top_positive = country_summary.nlargest(10, "positive_line_amount")
top_positive = top_positive.sort_values("positive_line_amount")

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(top_positive["country"], top_positive["positive_line_amount"])
ax.set_title("Top 10 Countries by Positive Line Amount")
ax.set_xlabel("Positive Line Amount")
ax.set_ylabel("Country")
ax.grid(axis="x", linestyle="--", alpha=0.3)
fig.tight_layout()
fig.savefig(
    CHARTS_DIR / "top_countries_by_positive_amount.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close(fig)

# Exclude the United Kingdom to compare international markets more clearly.
international = country_summary[
    country_summary["country"] != "United Kingdom"
]
top_international = international.nlargest(
    10, "positive_line_amount"
).sort_values("positive_line_amount")

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(
    top_international["country"],
    top_international["positive_line_amount"],
)
ax.set_title("Top 10 International Countries by Positive Line Amount")
ax.set_xlabel("Positive Line Amount")
ax.set_ylabel("Country")
ax.grid(axis="x", linestyle="--", alpha=0.3)
fig.tight_layout()
fig.savefig(
    CHARTS_DIR / "top_international_countries_by_positive_amount.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close(fig)

# Display the main findings in the terminal.
print("Country analysis completed successfully.")
print(f"Dataset rows: {len(df):,}")
print(f"Countries analyzed: {country_summary['country'].nunique()}")
print(f"Country summary saved to: {OUTPUT_FILE}")
print(f"Charts saved to: {CHARTS_DIR}")

print("\n=== TOP 10 COUNTRIES BY TRANSACTION LINES ===")
print(
    country_summary.nlargest(10, "transaction_lines")[
        ["country", "transaction_lines", "transaction_line_share_pct"]
    ].to_string(index=False)
)

print("\n=== TOP 10 COUNTRIES BY POSITIVE LINE AMOUNT ===")
print(
    country_summary.nlargest(10, "positive_line_amount")[
        ["country", "positive_line_amount", "negative_line_amount",
         "net_line_amount"]
    ].to_string(index=False)
)

print("\n=== TOP 10 INTERNATIONAL COUNTRIES BY POSITIVE LINE AMOUNT ===")
print(
    international.nlargest(10, "positive_line_amount")[
        ["country", "positive_line_amount", "negative_line_amount",
         "net_line_amount"]
    ].to_string(index=False)
)
