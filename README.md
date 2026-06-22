# Diabetes Analytics Platform

## Project Overview

This project builds a diabetes analytics platform on Databricks using the **Medallion Architecture** (Bronze → Silver → Gold), combining two diverse data sources to serve two distinct business objectives, culminating in a unified SQL dashboard.

## Business Objectives

| **Obj1** | **Population Risk Profiling** – Identify demographic and lifestyle segments with highest diabetes prevalence to support preventive care targeting | CDC BRFSS Dataset |

| **Obj2** | **Hospital Readmission Reduction** – Detect clinical and treatment drivers of 30-day diabetic patient readmissions | UCI 130-US Hospitals Dataset |

## Data Sources

### Source 1 – Object Storage (CSV)
**CDC Behavioral Risk Factor Surveillance System (BRFSS) 2015 – Diabetes Health Indicators**
- UCI ML Repository ID: 891
- URL: https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators
- Kaggle: https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset
- 22 features: BMI, blood pressure, cholesterol, physical activity, age, income, gender, diabetes label
- File: `data/cdc_brfss_diabetes.csv`

### Source 2 – Structured / Database
**Diabetes 130-US Hospitals for Years 1999-2008**
- UCI ML Repository ID: 296
- URL: https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008
- Citation: Strack B. et al. (2014). BioMed Research International.
- 30 features: patient demographics, admission details, diagnoses, medications, readmission status
- File: `data/diabetes_hospitals.csv`

## Notebooks 

| `00_setup.py` | Create database, DBFS paths | Setup |
| `01_bronze_ingest_brfss.py` | Ingest CDC BRFSS CSV (Data Source 1) → Delta | Bronze |
| `02_bronze_ingest_hospitals.py` | Ingest Hospital CSV (Data Source 2) → Delta | Bronze |
| `03_silver_transform_brfss.py` | Clean, decode, risk-score BRFSS | Silver |
| `04_silver_transform_hospitals.py` | Clean, derive features, flag readmissions | Silver |
| `05_gold_risk_profiling.py` | Objective 1 aggregations for dashboard | Gold |
| `06_gold_readmission_analysis.py` | Objective 2 aggregations for dashboard | Gold |

# How to Run

1. **Upload data files** to Databricks DBFS:
   - `dbfs:/FileStore/diabetes_project/raw/cdc_brfss_diabetes.csv`
   - `dbfs:/FileStore/diabetes_project/raw/diabetes_hospitals.csv`

2. **Import notebooks** into your Databricks workspace:
   - Go to **Workspace** → **Import** → upload each `.py` file

3. **Run notebooks in order** (00 → 01 → 02 → 03 → 04 → 05 → 06 → 07):
   - Run each notebook sequentially

## Live Dashboard
https://dbc-feeb6770-cc53.cloud.databricks.com/dashboardsv3/01f16bea5c5d1b08959cb224b131eeba/published?o=7474658464271415

## Testing the Pipeline
To verify the pipeline updates automatically when new data is added:

1. Clone this repo
2. Set up a free Databricks workspace at databricks.com
3. Upload the CSVs from the /data folder to a Unity Catalog Volume
4. Run notebooks 00 → 06 in order
5. Dashboard will automatically reflect new data

#Testing Performed

1. The High Risk Count was initially 339.
2. Inserted a test data of 10 rows.
3. The value of High Risk Count rose to 349.
[Kindly check the screenshots folders for the images]


## References

1. Teboul, A. (2021). *Diabetes Health Indicators Dataset*. UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators

2. Strack, B., DeShazo, J.P., Gennings, C., Olmo, J.L., Ventura, S., Cios, K.J., & Clore, J.N. (2014). Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records. *BioMed Research International*, 2014. https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008

