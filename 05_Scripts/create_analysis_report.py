
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether,
)

# ============================================================
# 1. PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "03_Results"
CHARTS = RESULTS / "Graficas"
DOCS = ROOT / "04_Documentation"

OUTPUT = DOCS / "Online_Retail_II_Analysis_Report.pdf"

DOCS.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. INPUT FILES
# ============================================================

INPUT_FILES = {
    "monthly": RESULTS / "monthly_sales_overview.csv",
    "countries": RESULTS / "country_sales_overview.csv",
    "products": RESULTS / "product_sales_overview.csv",
}

for name, path in INPUT_FILES.items():
    if not path.exists():
        raise FileNotFoundError(
            f"Required input file not found ({name}): {path}"
        )

monthly = pd.read_csv(INPUT_FILES["monthly"])
countries = pd.read_csv(INPUT_FILES["countries"])
products = pd.read_csv(INPUT_FILES["products"])


# ============================================================
# 3. REPORT STYLES
# ============================================================

NAVY = colors.HexColor("#243447")
BLUE = colors.HexColor("#36566F")
LIGHT_GREY = colors.HexColor("#F2F5F8")
MID_GREY = colors.HexColor("#D5DDE5")
DARK_GREY = colors.HexColor("#555555")

styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    name="ReportTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=23,
    leading=29,
    alignment=TA_CENTER,
    textColor=NAVY,
    spaceAfter=16,
))

styles.add(ParagraphStyle(
    name="Subtitle",
    parent=styles["Heading2"],
    fontSize=12,
    leading=17,
    alignment=TA_CENTER,
    textColor=BLUE,
    spaceAfter=18,
))

styles.add(ParagraphStyle(
    name="SectionHeading",
    parent=styles["Heading1"],
    fontSize=15,
    leading=19,
    textColor=NAVY,
    spaceBefore=10,
    spaceAfter=8,
))

styles.add(ParagraphStyle(
    name="SubHeading",
    parent=styles["Heading2"],
    fontSize=11,
    leading=14,
    textColor=BLUE,
    spaceBefore=7,
    spaceAfter=5,
))

styles.add(ParagraphStyle(
    name="ReportBody",
    parent=styles["BodyText"],
    fontSize=9,
    leading=13,
    spaceAfter=7,
))

styles.add(ParagraphStyle(
    name="SmallNote",
    parent=styles["BodyText"],
    fontSize=7.5,
    leading=10,
    textColor=DARK_GREY,
    spaceAfter=5,
))

story = []


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def format_number(value):
    """Format a number with thousands separators and two decimals."""
    return f"{float(value):,.2f}"


def add_bullet(text):
    """Add a bullet paragraph to the report."""
    story.append(
        Paragraph(f"&bull; {text}", styles["ReportBody"])
    )


def add_table(data, widths, font_size=7.5):
    """Add a styled table with a repeating header row."""
    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.35, MID_GREY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, LIGHT_GREY]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    story.append(table)
    story.append(Spacer(1, 9))


def add_chart(filename, caption, max_width=16.5 * cm):
    """Add a chart if it exists, preserving its aspect ratio."""
    path = CHARTS / filename

    if not path.exists():
        add_bullet(
            f"Chart not available: {filename}. "
            "The corresponding image file was not found."
        )
        return

    chart = Image(str(path))
    original_width = chart.imageWidth
    original_height = chart.imageHeight

    if original_width <= 0 or original_height <= 0:
        add_bullet(f"Chart could not be sized: {filename}")
        return

    ratio = original_height / original_width
    width = min(max_width, 17 * cm)
    height = width * ratio

    max_height = 9.5 * cm

    if height > max_height:
        height = max_height
        width = height / ratio

    story.append(Image(str(path), width=width, height=height))
    story.append(Paragraph(caption, styles["SmallNote"]))
    story.append(Spacer(1, 7))


def add_page_footer(canvas, doc):
    """Add a footer with project name and page number."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK_GREY)

    canvas.drawString(
        2 * cm,
        1.05 * cm,
        "Online Retail II | Data Analysis",
    )

    canvas.drawRightString(
        A4[0] - 2 * cm,
        1.05 * cm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


def require_columns(dataframe, required, filename):
    """Stop with a clear message if expected columns are missing."""
    missing = [column for column in required
               if column not in dataframe.columns]

    if missing:
        raise ValueError(
            f"Missing columns in {filename}: {missing}"
        )


# Validate the expected output schemas.
require_columns(
    monthly,
    [
        "month",
        "transaction_lines",
        "unique_invoices",
        "line_amount_total",
    ],
    "monthly_sales_overview.csv",
)

require_columns(
    countries,
    [
        "country",
        "transaction_lines",
        "positive_line_amount",
    ],
    "country_sales_overview.csv",
)

require_columns(
    products,
    [
        "stock_code",
        "description",
        "transaction_lines",
        "unique_invoices",
        "positive_line_amount",
        "negative_line_amount",
        "net_line_amount",
    ],
    "product_sales_overview.csv",
)


# ============================================================
# 5. COVER PAGE
# ============================================================

story.append(Spacer(1, 2.2 * cm))

story.append(Paragraph(
    "Online Retail II<br/>Data Analysis Report",
    styles["ReportTitle"],
))

story.append(Paragraph(
    "Transaction Patterns, Geographic Markets, "
    "and Product Performance",
    styles["Subtitle"],
))

story.append(Spacer(1, 0.5 * cm))

story.append(Paragraph(
    "<b>Project objective</b><br/>"
    "Identify sales-related patterns in the Online Retail II dataset "
    "and translate the findings into practical questions and "
    "opportunities for commercial improvement.",
    styles["ReportBody"],
))

story.append(Paragraph(
    "<b>Analytical scope</b><br/>"
    "This report summarizes data preparation, monthly transaction "
    "patterns, geographic distribution, and product-level results. "
    "It uses previously generated datasets and visualizations.",
    styles["ReportBody"],
))

story.append(Paragraph(
    "<b>Measurement note</b><br/>"
    "Line amount is calculated as quantity multiplied by unit price. "
    "Because the source contains cancellations, adjustments, and "
    "exceptional transactions, line amounts should not automatically "
    "be interpreted as verified net revenue or profit.",
    styles["ReportBody"],
))

story.append(Spacer(1, 1 * cm))

story.append(Paragraph(
    "Prepared as a data analyst portfolio project",
    styles["SmallNote"],
))

story.append(PageBreak())


# ============================================================
# 6. DATA AND METHODOLOGY
# ============================================================

story.append(Paragraph(
    "1. Data and Methodology",
    styles["SectionHeading"],
))

story.append(Paragraph(
    "The original workbook contains two yearly sheets with an "
    "overlapping date period in December 2010. During preparation, "
    "22,523 matching transaction rows were identified in the overlap "
    "and removed from the earlier sheet's overlapping period in the "
    "analysis dataset. The original workbook was preserved.",
    styles["ReportBody"],
))

data_summary = [
    ["Dataset stage", "Rows", "Purpose"],
    [
        "Combined standardized data",
        "1,067,371",
        "Standardized source records and calculated line amounts",
    ],
    [
        "Prepared analysis data",
        "1,044,848",
        "Analysis dataset after handling the identified overlap",
    ],
]

add_table(
    data_summary,
    [4.0 * cm, 3.0 * cm, 9.0 * cm],
)

story.append(Paragraph(
    "Data preparation and quality considerations",
    styles["SubHeading"],
))

for text in [
    "The source contains missing customer IDs and product descriptions.",
    "Cancellation records and negative quantities were retained for investigation.",
    "Some stock codes represent postage, fees, or adjustments rather than physical products.",
    "Some stock codes have multiple descriptions; descriptions were not automatically corrected.",
    "Exceptional positive and negative transactions were investigated rather than silently deleted.",
]:
    add_bullet(text)

story.append(Paragraph(
    "The separate Online Retail II Data Quality Report documents "
    "the detailed quality checks, exceptional cases, and preparation "
    "decisions.",
    styles["ReportBody"],
))


# ============================================================
# 7. MONTHLY ANALYSIS
# ============================================================

story.append(Paragraph(
    "2. Monthly Transaction Patterns",
    styles["SectionHeading"],
))

story.append(Paragraph(
    "Monthly results show changes in transaction activity and line "
    "amounts over time. November has high activity in both observed "
    "years. This is a pattern worth investigating, but two years of "
    "observations are not sufficient to establish a stable seasonal effect.",
    styles["ReportBody"],
))

for month_value in ["2010-11", "2011-11", "2011-12"]:
    matched = monthly[
        monthly["month"].astype(str) == month_value
    ]

    if matched.empty:
        continue

    row = matched.iloc[0]

    story.append(Paragraph(
        f"<b>{month_value}</b>: "
        f"{int(row['transaction_lines']):,} transaction lines; "
        f"{int(row['unique_invoices']):,} unique invoices; "
        f"line amount total {format_number(row['line_amount_total'])}.",
        styles["ReportBody"],
    ))

story.append(Paragraph(
    "December 2011 is incomplete, with source records ending on "
    "December 9. It should not be compared with complete months as "
    "if it represented a full month. Large cancellation-related "
    "amounts also affect some monthly totals.",
    styles["ReportBody"],
))

add_chart(
    "monthly_line_amount_trends.png",
    "Figure 1. Monthly line amount totals. Interpret peaks alongside "
    "cancellations, exceptional transactions, and incomplete periods.",
)

add_chart(
    "monthly_transaction_activity.png",
    "Figure 2. Monthly transaction activity.",
)

add_chart(
    "monthly_negative_amounts.png",
    "Figure 3. Monthly negative line amounts, highlighting periods "
    "that warrant further review.",
)

story.append(PageBreak())


# ============================================================
# 8. GEOGRAPHIC ANALYSIS
# ============================================================

story.append(Paragraph(
    "3. Geographic Distribution",
    styles["SectionHeading"],
))

uk_rows = countries[
    countries["country"].astype(str) == "United Kingdom"
]

if not uk_rows.empty:
    uk_count = int(uk_rows.iloc[0]["transaction_lines"])
    total_lines = int(countries["transaction_lines"].sum())
    uk_share = (
        uk_count / total_lines * 100
        if total_lines else 0
    )

    story.append(Paragraph(
        f"The United Kingdom accounts for {uk_count:,} transaction "
        f"lines, approximately {uk_share:.2f}% of the country-level "
        "transaction-line total.",
        styles["ReportBody"],
    ))

story.append(Paragraph(
    "EIRE and Germany are among the next largest markets by "
    "transaction-line count, while EIRE and the Netherlands rank "
    "highly by positive line amount. The difference between these "
    "rankings suggests that transaction frequency and positive line "
    "amount provide complementary views of market activity.",
    styles["ReportBody"],
))

story.append(Paragraph(
    "The concentration in the UK suggests that the observed business "
    "activity is heavily dependent on that market. International markets "
    "may warrant further investigation, but expansion decisions would "
    "require evidence on customer acquisition, delivery costs, margins, "
    "and market potential.",
    styles["ReportBody"],
))

country_table = [
    ["Country", "Transaction lines", "Positive line amount"],
]

for country_name in [
    "United Kingdom",
    "EIRE",
    "Germany",
    "France",
    "Netherlands",
]:
    matched = countries[
        countries["country"].astype(str) == country_name
    ]

    if matched.empty:
        continue

    row = matched.iloc[0]

    country_table.append([
        str(row["country"]),
        f"{int(row['transaction_lines']):,}",
        format_number(row["positive_line_amount"]),
    ])

add_table(
    country_table,
    [4.5 * cm, 4.0 * cm, 5.0 * cm],
)

add_chart(
    "top_countries_by_transaction_lines.png",
    "Figure 4. Countries ranked by transaction-line count.",
)

add_chart(
    "top_countries_by_positive_amount.png",
    "Figure 5. Countries ranked by positive line amount.",
)

add_chart(
    "top_international_countries_by_positive_amount.png",
    "Figure 6. Leading international markets by positive line amount.",
)

story.append(PageBreak())


# ============================================================
# 9. PRODUCT ANALYSIS
# ============================================================

story.append(Paragraph(
    "4. Product-Level Findings",
    styles["SectionHeading"],
))

story.append(Paragraph(
    "Product comparisons exclude known non-standard stock codes and "
    "two previously investigated exceptional product codes. This "
    "filter is used only for comparative rankings; it does not remove "
    "records from the underlying prepared dataset.",
    styles["ReportBody"],
))

excluded_codes = {
    "M", "DOT", "POST", "AMAZONFEE", "BANK CHARGES",
    "ADJUST", "ADJUST2", "B", "D", "CRUK", "C2", "PADS", "S",
    "23843", "23166",
}

normalized_codes = (
    products["stock_code"].astype(str).str.upper().str.strip()
)

physical_products = products.loc[
    ~normalized_codes.isin(excluded_codes)
].copy()

story.append(Paragraph(
    "Top 10 Products by Positive Line Amount",
    styles["SubHeading"],
))

amount_table = [
    ["Stock code", "Product", "Lines", "Positive amount"],
]

for _, row in physical_products.nlargest(
    10, "positive_line_amount"
).iterrows():
    amount_table.append([
        str(row["stock_code"]),
        str(row["description"])[:45],
        f"{int(row['transaction_lines']):,}",
        format_number(row["positive_line_amount"]),
    ])

add_table(
    amount_table,
    [2.0 * cm, 7.0 * cm, 2.0 * cm, 3.5 * cm],
)

story.append(Paragraph(
    "Top 10 Products by Transaction-Line Frequency",
    styles["SubHeading"],
))

frequency_table = [
    ["Stock code", "Product", "Lines", "Unique invoices"],
]

for _, row in physical_products.nlargest(
    10, "transaction_lines"
).iterrows():
    frequency_table.append([
        str(row["stock_code"]),
        str(row["description"])[:45],
        f"{int(row['transaction_lines']):,}",
        f"{int(row['unique_invoices']):,}",
    ])

add_table(
    frequency_table,
    [2.0 * cm, 7.0 * cm, 2.0 * cm, 3.5 * cm],
)

story.append(Paragraph(
    "Regency Cakestand 3 Tier has the highest positive line amount "
    "in the filtered comparison. White Hanging Heart T-Light Holder "
    "has the highest transaction-line count and appears in the most "
    "unique invoices among the listed products. Jumbo Bag Red Retrospot "
    "also ranks highly on both measures.",
    styles["ReportBody"],
))

story.append(Paragraph(
    "These findings show that product frequency and positive line "
    "amount are different indicators. Neither metric establishes "
    "profitability, and both must be interpreted alongside returns, "
    "cancellations, and the limitations of the source data.",
    styles["ReportBody"],
))

story.append(PageBreak())


# ============================================================
# 10. BUSINESS OPPORTUNITIES
# ============================================================

story.append(Paragraph(
    "5. Business Opportunities",
    styles["SectionHeading"],
))

recommendations = [
    (
        "Review product availability",
        "Use frequently purchased products as candidates for stock "
        "availability and replenishment reviews, subject to inventory "
        "and supply data."
    ),
    (
        "Investigate international markets",
        "Compare selected international markets using customer counts, "
        "order values, delivery costs, and margins before recommending "
        "expansion."
    ),
    (
        "Monitor cancellations and adjustments",
        "Report exceptional cancellations separately so unusual "
        "transactions do not distort product or monthly comparisons."
    ),
    (
        "Improve product data governance",
        "Review stock codes with conflicting or missing descriptions "
        "and distinguish physical products from charges and adjustments."
    ),
    (
        "Validate seasonal hypotheses",
        "Analyze additional complete years before drawing conclusions "
        "about seasonality or making calendar-based sales forecasts."
    ),
]

for title, description in recommendations:
    story.append(KeepTogether([
        Paragraph(title, styles["SubHeading"]),
        Paragraph(description, styles["ReportBody"]),
    ]))


# ============================================================
# 11. LIMITATIONS AND CONCLUSION
# ============================================================

story.append(Paragraph(
    "6. Limitations",
    styles["SectionHeading"],
))

for text in [
    "The dataset represents historical activity and may not reflect current behavior.",
    "December 2011 is incomplete.",
    "Missing customer IDs limit customer-level analysis.",
    "Line amounts do not establish profit or verified net revenue.",
    "Observed rankings and patterns do not prove causation or future demand.",
    "Business recommendations require additional operational and financial data.",
]:
    add_bullet(text)

story.append(Paragraph(
    "7. Conclusion",
    styles["SectionHeading"],
))

story.append(Paragraph(
    "The analysis identifies a highly concentrated UK market, months "
    "with elevated transaction activity, and products that stand out "
    "by frequency or positive line amount. The main value of the "
    "project is the combination of data preparation, quality checks, "
    "descriptive analysis, and cautious business interpretation. "
    "Further operational and financial data would be needed to validate "
    "the proposed commercial opportunities.",
    styles["ReportBody"],
))


# ============================================================
# 12. PROJECT OUTPUTS
# ============================================================

story.append(Paragraph(
    "8. Project Outputs",
    styles["SectionHeading"],
))

for item in [
    "03_Results/monthly_sales_overview.csv",
    "03_Results/country_sales_overview.csv",
    "03_Results/product_sales_overview.csv",
    "03_Results/Graficas/",
    "04_Documentation/Online_Retail_II_Data_Quality_Report.pdf",
]:
    add_bullet(item)


# ============================================================
# 13. BUILD PDF
# ============================================================

document = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    rightMargin=1.8 * cm,
    leftMargin=1.8 * cm,
    topMargin=1.7 * cm,
    bottomMargin=1.7 * cm,
    title="Online Retail II Data Analysis Report",
    author="Data Analyst Portfolio Project",
)

document.build(
    story,
    onFirstPage=add_page_footer,
    onLaterPages=add_page_footer,
)

print("Analysis report created successfully.")
print(f"Output file: {OUTPUT}")
print(f"File exists: {OUTPUT.exists()}")

if OUTPUT.exists():
    print(f"File size: {OUTPUT.stat().st_size:,} bytes")
