# Online Retail II — Data Analysis Project

## Project Overview

This project analyzes retail transaction data to identify patterns in sales activity, product performance, geographic distribution, and transaction quality.

The main business question is:

**What sales, product, and purchasing behavior patterns can be identified to uncover commercial improvement opportunities?**

The project emphasizes data preparation, data quality validation, exploratory analysis, and evidence-based recommendations.

## Objectives

- Consolidate transaction records from two reporting periods.
- Identify and handle overlapping dates between source periods.
- Assess missing values, duplicate records, cancellations, and unusual transaction values.
- Analyze monthly transaction activity and line amounts.
- Compare geographic activity and product performance.
- Communicate findings through charts and PDF reports.

## Tools and Technologies

- Python
- pandas
- NumPy
- Matplotlib
- Excel
- PowerShell

## Dataset

The source workbook contains two worksheets:

- `Year 2009-2010`
- `Year 2010-2011`

The combined source data contains 1,067,371 rows and 8 original columns.

The analysis preparation process standardizes column names, preserves important identifiers, records the source period, and calculates transaction line amounts.

The two source periods overlap from December 1 to December 9, 2010. To avoid counting this period twice, 22,523 rows from the earlier source period were excluded from the final analysis dataset.

The resulting analysis dataset contains **1,044,848 rows**.

The original workbook and large intermediate datasets are not included in this repository. The source file should be obtained from its original provider, subject to the provider's access and redistribution terms.

## Data Preparation and Quality

The project includes scripts to:

1. Inspect the source workbook and profile the data.
2. Consolidate both worksheets into a standardized dataset.
3. Validate dataset structure, missing values, dates, and transaction values.
4. Create data quality flags without automatically deleting flagged records.
5. Investigate duplicate records, cancellations, negative amounts, and unusual transactions.
6. Exclude the overlapping dates from the earlier source period.
7. Produce analysis-ready data and supporting diagnostic outputs.

Quality checks include:

- Missing customer identifiers and product descriptions.
- Negative quantities and zero or negative prices.
- Invoice identifiers beginning with `C`.
- Exact duplicate rows and repeated occurrences.
- Invalid dates and transaction line amount consistency.

A negative quantity, negative amount, or cancellation flag does not automatically establish the business reason for a transaction. These records require context and investigation.

## Analysis Areas

### 1. Monthly Activity

The monthly analysis examines transaction lines, unique invoices, quantities, and transaction line amounts. Additional outputs separate positive and negative amounts and summarize transaction quality.

Key observation:

- November 2011 had approximately 2.67% more positive transaction line amount than November 2010.

This comparison covers two Novembers only and does not establish a recurring seasonal pattern.

December 2011 is incomplete, with records ending on December 9, so it should not be compared directly with complete months.

### 2. Geographic Analysis

The country analysis compares transaction activity and positive transaction line amounts.

Key observations:

- The United Kingdom accounts for approximately 91.88% of transaction lines in the final analysis dataset.
- EIRE, the Netherlands, Germany, and France are among the other countries with substantial positive transaction line amounts.

The concentration of activity in the United Kingdom suggests that geographic performance should be interpreted in the context of the dataset's existing market distribution.

### 3. Product Analysis

The product analysis examines transaction frequency and positive transaction line amounts.

Key observations:

- `WHITE HANGING HEART T-LIGHT HOLDER` has the highest transaction-line count among the products analyzed.
- `REGENCY CAKESTAND 3 TIER` has the highest positive transaction line amount in the filtered product ranking.
- `JUMBO BAG RED RETROSPOT` performs strongly across both transaction frequency and positive line amount.

Special stock codes and two investigated extreme transactions are excluded from the filtered monetary ranking. This filter is used for comparative analysis; it does not delete records from the source dataset.

Transaction frequency and positive line amount are not measures of profitability. The dataset does not provide all the cost and business information needed to calculate profit.

## Key Findings and Business Implications

- **Market concentration:** The United Kingdom dominates transaction activity. Further analysis could compare customer behavior and product preferences across geographic markets.
- **Product performance:** Frequently purchased products and products with high positive line amounts may warrant further investigation for merchandising and inventory planning.
- **Transaction quality:** Cancellations, negative quantities, missing customer identifiers, and duplicate records can materially affect commercial reporting.
- **Monthly comparisons:** Changes in transaction line amounts should be interpreted alongside negative amounts, cancellations, and data completeness.

These findings identify opportunities for further investigation rather than proving causation or guaranteeing future performance.

## Reports and Visualizations

### PDF Reports

- [Full Analysis Report](04_Documentation/Online_Retail_II_Analysis_Report.pdf)
- [Data Quality Report](04_Documentation/Online_Retail_II_Data_Quality_Report.pdf)

### Charts

The `03_Results/Graficas/` directory contains:

- Monthly transaction line amount trends.
- Monthly transaction activity.
- Monthly negative transaction line amounts.
- Top countries by transaction-line count.
- Top countries by positive transaction line amount.
- Leading international countries by positive transaction line amount.

Selected aggregated CSV outputs are also included in `03_Results/`.

## Repository Structure

```text
online-retail-ii-analysis/
├── .gitignore
├── README.md
├── 03_Results/
│   ├── Graficas/
│   └── aggregated analysis and diagnostic CSV files
├── 04_Documentation/
│   ├── Online_Retail_II_Analysis_Report.pdf
│   └── Online_Retail_II_Data_Quality_Report.pdf
└── 05_Scripts/
    ├── prepare_dataset.py
    ├── flag_data_quality.py
    ├── remove_period_overlap.py
    ├── validate_dataset.py
    ├── monthly analysis scripts
    ├── country_sales_analysis.py
    ├── product_sales_analysis.py
    └── investigation and reporting scripts
```

Large original and intermediate datasets are retained locally and are not intended for upload to this repository.

## Reproducing the Analysis

### Requirements

Python 3 and the following packages are used by the project:

- pandas
- NumPy
- openpyxl
- Matplotlib
- ReportLab

### Preparation Workflow

Place the source workbook at:

`01_Original_Data/online_retail_II.xlsx`

From the project root, run the scripts in the following order:

```powershell
python .\05_Scripts\prepare_dataset.py
python .\05_Scripts\validate_dataset.py
python .\05_Scripts\flag_data_quality.py
python .\05_Scripts\validate_flagged_dataset.py
python .\05_Scripts\remove_period_overlap.py
```

The validation script checks the consolidated dataset, while the flagged dataset has its own validation script. The overlap-removal script produces the final analysis dataset.

The analysis, visualization, and report-generation scripts depend on their required input files being available in the expected directories. Review each script's input and output paths before running it independently.

## Limitations

- Missing customer identifiers limit customer-level analysis.
- Cancellations and negative transaction amounts require careful interpretation.
- Exact duplicate records are identified, but not every repeated-looking transaction is necessarily erroneous.
- December 2011 covers only part of the month.
- Two annual observations of November are insufficient to establish seasonality.
- Positive transaction line amounts do not represent confirmed net revenue or profit.
- Product rankings depend on the documented stock-code and outlier filters.

## Conclusion

This project demonstrates a structured data analysis workflow that combines data preparation, quality checks, transaction investigations, descriptive analysis, visualization, and written reporting.

The results highlight geographic concentration, product-level patterns, and the importance of understanding transaction quality before drawing commercial conclusions.

The project also documents limitations and preserves flagged records for investigation rather than assuming that every anomaly should be removed.

---

*Portfolio project developed for data analytics practice and professional demonstration.*
