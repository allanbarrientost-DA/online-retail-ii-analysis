
"""
Create monthly sales and transaction visualizations for Online Retail II.
All charts are saved as PNG files in 03_Results/Graficas.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "03_Results"
CHARTS_DIR = RESULTS_DIR / "Graficas"

OVERVIEW_FILE = RESULTS_DIR / "monthly_sales_overview.csv"
COMPONENTS_FILE = RESULTS_DIR / "monthly_sales_components.csv"

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Load existing monthly results.
overview = pd.read_csv(OVERVIEW_FILE)
components = pd.read_csv(COMPONENTS_FILE)

# Parse month labels into dates and sort chronologically.
overview["month"] = pd.to_datetime(overview["month"], format="%Y-%m")
components["month"] = pd.to_datetime(
    components["month"], format="%Y-%m"
)

overview = overview.sort_values("month")
components = components.sort_values("month")

# Shared date-axis formatting.
def format_month_axis(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.35)


# Graph 1: Monthly positive, negative, and total line amounts.
fig, ax = plt.subplots(figsize=(13, 6))

ax.plot(
    components["month"],
    components["positive_amount_total"],
    marker="o",
    markersize=3,
    label="Positive Line Amount",
)
ax.plot(
    components["month"],
    components["negative_amount_total"],
    marker="o",
    markersize=3,
    label="Negative Line Amount",
)
ax.plot(
    components["month"],
    components["total_line_amount"],
    marker="o",
    markersize=3,
    label="Total Line Amount",
)

ax.set_title("Monthly Line Amount Trends")
ax.set_xlabel("Month")
ax.set_ylabel("Line Amount")
ax.legend()
format_month_axis(ax)

fig.tight_layout()
fig.savefig(
    CHARTS_DIR / "monthly_line_amount_trends.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close(fig)


# Graph 2: Monthly transaction-line activity.
fig, ax = plt.subplots(figsize=(13, 6))

ax.bar(
    overview["month"],
    overview["transaction_lines"],
    width=20,
)

ax.set_title("Monthly Transaction Activity")
ax.set_xlabel("Month")
ax.set_ylabel("Number of Transaction Lines")
format_month_axis(ax)

fig.tight_layout()
fig.savefig(
    CHARTS_DIR / "monthly_transaction_activity.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close(fig)


# Graph 3: Magnitude of negative line amounts by month.
fig, ax = plt.subplots(figsize=(13, 6))

ax.bar(
    components["month"],
    components["negative_amount_magnitude"],
    width=20,
)

ax.set_title("Monthly Negative Line Amount Magnitude")
ax.set_xlabel("Month")
ax.set_ylabel("Absolute Negative Line Amount")
format_month_axis(ax)

fig.tight_layout()
fig.savefig(
    CHARTS_DIR / "monthly_negative_amounts.png",
    dpi=300,
    bbox_inches="tight",
)
plt.close(fig)


print("Monthly visualizations created successfully.")
print(f"Output folder: {CHARTS_DIR}")
print("Generated files:")
print("- monthly_line_amount_trends.png")
print("- monthly_transaction_activity.png")
print("- monthly_negative_amounts.png")
