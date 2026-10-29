"""Generate an English-language Online Retail II data quality PDF report.
Run from project root:
  .\\.venv\\Scripts\\python.exe .\\05_Scripts\\create_data_quality_report.py
Output: 04_Documentation/Online_Retail_II_Data_Quality_Report.pdf
"""
from pathlib import Path
from datetime import datetime
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
except ImportError:
    raise SystemExit("ReportLab is required. Install it with: .\\.venv\\Scripts\\python.exe -m pip install reportlab")

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "04_Documentation"
OUTPUT = OUT_DIR / "Online_Retail_II_Data_Quality_Report.pdf"

SOURCE_ROWS = [
 ["Source sheet", "Rows", "Date range"],
 ["Year 2009-2010", "525,461", "2009-12-01 07:45 to 2010-12-09 20:01"],
 ["Year 2010-2011", "541,910", "2010-12-01 08:26 to 2011-12-09 12:50"],
]
QUALITY_ROWS = [
 ["Quality check (full combined dataset)", "Rows", "Share of 1,067,371"],
 ["Missing customer ID", "243,007", "22.77%"],
 ["Missing description", "4,382", "0.41%"],
 ["Cancellation invoice (starts with C)", "19,494", "1.83%"],
 ["Negative quantity", "22,950", "2.15%"],
 ["Zero unit price", "6,202", "0.58%"],
 ["Negative unit price", "5", "<0.01%"],
 ["Rows in exact-duplicate groups", "23,430", "2.20%"],
 ["Extra exact-duplicate occurrences", "12,133", "1.14%"],
]
RULE_ROWS = [
 ["Decision", "Rule applied / recommended treatment"],
 ["Preserve raw data", "Keep the original workbook unchanged; prepare copies."],
 ["Standardize schema", "Use consistent lowercase column names and retain source_period."],
 ["Line amount", "Calculate line_amount = quantity × unit_price; do not automatically call its sum net sales."],
 ["Period overlap", "Exclude 22,523 matching overlap rows from the 2009-2010 source period in the analysis dataset."],
 ["Quality flags", "Retain rows in the flagged dataset and add explicit flags instead of silently deleting questionable records."],
 ["Missing customer IDs", "Retain for product/country/date analyses; treat customer-level results cautiously."],
 ["Missing descriptions", "Do not automatically replace ambiguous descriptions; review candidate descriptions first."],
 ["Cancellations / returns", "Use invoice IDs, quantities, and amounts together; distinguish positive, negative, and net measures."],
 ["Duplicates", "Flag exact duplicates and investigate before deletion because repeated lines may be meaningful."],
 ["Extreme values", "Document business context before excluding exceptional records from a metric."],
]
FINDINGS = [
 ("Dataset preparation", "The two sheets contain 1,067,371 records. The standardized combined dataset has 10 columns, including source_period and line_amount. Each line amount is quantity multiplied by unit price."),
 ("Missing values", "Customer IDs are missing in 243,007 rows (22.77%). Such rows may still support product, country, and date analyses but not reliable customer identification. Descriptions are missing in 4,382 rows (0.41%)."),
 ("Description investigation", "Of 4,382 rows with missing descriptions, 4,019 had the same stock code with a non-empty description elsewhere and 363 did not. Across 2,451 affected stock codes, 2,096 had at least one candidate description and 355 had none. Some stock codes have conflicting descriptions, so automatic replacement is unsafe without review."),
 ("Negative amounts", "In the analysis dataset after overlap removal, 19,169 rows have negative line amounts. Of these, 19,164 have cancellation invoice IDs beginning with C and negative quantities. Five negative-amount rows have negative unit prices; categories overlap and are not mutually exclusive."),
 ("Overlapping source periods", "The sheets overlap from 2010-12-01 through 2010-12-09. Investigation identified 22,523 matching transaction rows. The analysis dataset excludes these rows from the 2009-2010 source period only, retaining 1,044,848 rows. The original workbook and full flagged dataset are preserved."),
 ("Extreme cancellation pair", "On 2011-12-09, invoice 581483 records +80,995 units of stock code 23843 at 2.08 per unit (+168,469.60), followed 12 minutes later by cancellation invoice C581484 for -80,995 units and -168,469.60. Customer, product, country, quantity magnitude, and amount magnitude match. Document the pair rather than automatically removing it from every analysis."),
 ("Incomplete final month", "December 2011 ends on 2011-12-09 12:50 and is incomplete. Do not compare it directly with complete months without qualification or an adjusted comparison window."),
]
LIMITATIONS = [
 "Rows represent transaction lines, not necessarily distinct orders or customers.",
 "Missing customer IDs limit customer-level analysis and repeat-purchase identification.",
 "The sum of line_amount is not automatically net sales because cancellations, adjustments, and exceptional records are included.",
 "Some zero- or negative-price records may represent fees, adjustments, samples, or data-quality issues and require context.",
 "The source periods overlap and the final month is incomplete; comparisons must account for both.",
 "The dataset is historical and should not be assumed to represent current retail behavior.",
]
FILES = [
 ["File", "Purpose"],
 ["02_Processed_Data/online_retail_combined.csv", "Standardized combined dataset before overlap removal."],
 ["02_Processed_Data/online_retail_flagged.csv", "Combined dataset with quality flags."],
 ["02_Processed_Data/online_retail_analysis.csv", "Analysis dataset after removing identified overlap."],
 ["04_Documentation/description_candidates.csv", "Candidate descriptions for stock codes with missing descriptions."],
 ["03_Results/monthly_sales_overview.csv", "Monthly transaction and line-amount overview."],
 ["03_Results/monthly_sales_components.csv", "Monthly positive, negative, and zero line-amount components."],
 ["03_Results/negative_amount_diagnostics.csv", "Diagnostics for negative line amounts."],
]

def table(rows, widths, size=8):
    t=Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
      ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#263746")),
      ("TEXTCOLOR",(0,0),(-1,0),colors.white), ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
      ("FONTNAME",(0,1),(-1,-1),"Helvetica"), ("FONTSIZE",(0,0),(-1,-1),size),
      ("LEADING",(0,0),(-1,-1),size+2), ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#D2D8DE")),
      ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),5),
      ("RIGHTPADDING",(0,0),(-1,-1),5), ("TOPPADDING",(0,0),(-1,-1),5),
      ("BOTTOMPADDING",(0,0),(-1,-1),5),
      ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F3F6F8")]),
    ])); return t

def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica",8); canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2*cm,1.1*cm,"Online Retail II | Data Quality Report")
    canvas.drawRightString(A4[0]-2*cm,1.1*cm,f"Page {doc.page}"); canvas.restoreState()

def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    s=getSampleStyleSheet()
    s.add(ParagraphStyle(name="CoverTitle",parent=s["Title"],fontName="Helvetica-Bold",fontSize=23,leading=28,alignment=TA_CENTER,textColor=colors.HexColor("#263746"),spaceAfter=10))
    s.add(ParagraphStyle(name="Section",parent=s["Heading2"],fontName="Helvetica-Bold",fontSize=13,leading=16,textColor=colors.HexColor("#263746"),spaceBefore=10,spaceAfter=6))
    s.add(ParagraphStyle(name="BodySmall",parent=s["BodyText"],fontSize=8.8,leading=12,spaceAfter=5))
    story=[]
    def para(txt, style="BodySmall"): story.append(Paragraph(txt,s[style]))
    story += [Spacer(1,2*cm),Paragraph("ONLINE RETAIL II",s["CoverTitle"]),Paragraph("Data Quality and Preparation Report",s["Heading1"]),Spacer(1,.5*cm),Paragraph("Python-generated portfolio report",s["BodyText"]),Spacer(1,.2*cm),Paragraph("Report generated: "+datetime.now().strftime("%Y-%m-%d"),s["BodyText"]),Spacer(1,1*cm)]
    para("Purpose: document dataset structure, quality issues, preparation decisions, exceptional transactions, and limitations affecting downstream sales analysis.")
    story.append(table([["Dataset milestone","Validated value"],["Original source records","1,067,371"],["Rows removed for identified period overlap","22,523"],["Rows in analysis dataset","1,044,848"],["Original columns","8"],["Standardized prepared columns","10"]],[8*cm,8*cm],9))
    story.append(PageBreak())
    para("1. Executive Summary","Section")
    para("The Online Retail II workbook contains two source sheets covering December 2009 through December 2011. Preparation standardized the schema, created a line amount, preserved quality flags, investigated missing descriptions and negative amounts, and removed a confirmed overlap between the source periods. The final analysis dataset contains 1,044,848 rows. Questionable records were investigated and documented rather than indiscriminately deleted.")
    para("2. Source Data","Section"); story.append(table(SOURCE_ROWS,[3.4*cm,2*cm,10.6*cm],7.3))
    para("Original fields: Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, and Country. The standardized dataset uses lowercase names and adds source_period and line_amount.")
    para("3. Data Quality Findings","Section"); story.append(table(QUALITY_ROWS,[7.2*cm,2.2*cm,6.6*cm],7.2))
    para("These quality counts describe the full combined flagged dataset (1,067,371 rows), before overlap removal. Categories may overlap; cancellation invoices commonly also have negative quantities.")
    para("4. Key Investigations","Section")
    for title,body in FINDINGS:
        story.append(KeepTogether([Paragraph(title,s["Heading3"]),Paragraph(body,s["BodySmall"])]))
    story.append(PageBreak())
    para("5. Preparation Rules and Decisions","Section"); story.append(table(RULE_ROWS,[3.6*cm,12.4*cm],7.4))
    para("6. Limitations and Analytical Risks","Section")
    for x in LIMITATIONS: para("• "+x)
    para("7. Recommended Next Steps","Section")
    for x in ["Define each business metric before filtering records (for example, positive line value, cancellations, or net line value).","For every KPI or chart, document whether cancellations, zero-price rows, adjustments, and missing customer IDs are included.","Use comparable complete months for monthly trends and label December 2011 as partial.","Continue analysis of monthly patterns, countries, products, invoices, and customer behavior where IDs are available.","Create a data dictionary and README describing the workflow and known limitations.","Keep reproducible scripts and derived outputs in their project folders; check data-sharing terms before publishing raw data."]: para("• "+x)
    para("8. Project Files Referenced","Section"); story.append(table(FILES,[7.2*cm,8.8*cm],7.2))
    story.append(Spacer(1,.25*cm)); para("This report summarizes validated findings recorded during the project workflow. If the data or cleaning rules change, rerun the relevant validation scripts and update this report before publishing it as a portfolio artifact.")
    doc=SimpleDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=2*cm,leftMargin=2*cm,topMargin=1.7*cm,bottomMargin=1.7*cm,title="Online Retail II - Data Quality and Preparation Report",author="Data Analyst Portfolio Project")
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print("Report created successfully.")
    print(f"Output: {OUTPUT}")
    print(f"File exists: {OUTPUT.exists()}")
    if OUTPUT.exists(): print(f"File size: {OUTPUT.stat().st_size:,} bytes")

if __name__ == "__main__": build()
