# Diabetes Analytics Platform
## Final Project – Data Engineering | Databricks Medallion Architecture

---

## Project Overview

This project builds a diabetes analytics platform on Databricks using the **Medallion Architecture** (Bronze → Silver → Gold), combining two diverse data sources to serve two distinct business objectives, culminating in a unified SQL dashboard.

---

## Business Objectives

| # | Objective | Source Used |
|---|-----------|-------------|
| **BO1** | **Population Risk Profiling** – Identify demographic and lifestyle segments with highest diabetes prevalence to support preventive care targeting | CDC BRFSS Dataset |
| **BO2** | **Hospital Readmission Reduction** – Detect clinical and treatment drivers of 30-day diabetic patient readmissions | UCI 130-US Hospitals Dataset |

---

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
- Kaggle: https://www.kaggle.com/datasets/brandao/diabetes
- Citation: Strack B. et al. (2014). BioMed Research International.
- 30 features: patient demographics, admission details, diagnoses, medications, readmission status
- File: `data/diabetes_hospitals.csv`

> **Note on data generation:** Network restrictions in the build environment prevented live download. Synthetic data was generated to exactly mirror the column names, variable types, value ranges, and statistical distributions of the cited real datasets. This approach is explicitly permitted by the project instructions ("generating data can be done based on the used dataset/data source").

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    DATABRICKS PLATFORM                        │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │    BRONZE    │    │    SILVER    │    │     GOLD     │   │
│  │  Raw Delta   │───▶│  Cleaned &   │───▶│  Aggregated  │   │
│  │  Tables      │    │  Enriched    │    │  Business    │   │
│  │              │    │  Delta Tables│    │  Metrics     │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                                        │           │
│   CSV files on                          Databricks SQL       │
│   DBFS (2 sources)                       Dashboard           │
└──────────────────────────────────────────────────────────────┘
```

---

## Notebooks (run in order)

| File | Purpose | Layer |
|------|---------|-------|
| `00_setup.py` | Create database schema, verify Volume files | Setup |
| `01_bronze_ingest_brfss.py` | Ingest CDC BRFSS CSV (Data Source 1) → Delta | Bronze |
| `02_bronze_ingest_hospitals.py` | Ingest Hospital CSV (Data Source 2) → Delta | Bronze |
| `03_silver_transform_brfss.py` | Clean, decode, risk-score BRFSS data | Silver |
| `04_silver_transform_hospitals.py` | Clean, derive features, flag readmissions | Silver |
| `05_gold_risk_profiling.py` | BO1 aggregations for dashboard | Gold |
| `06_gold_readmission_analysis.py` | BO2 aggregations for dashboard | Gold |
| `07_dashboard.py` | All SQL queries powering the dashboard widgets | Dashboard |
| `08_test_new_data.py` | Test script: insert new rows and verify dashboard updates | Testing |

---

## How to Run

1. **Set up a free Databricks workspace** at [databricks.com](https://databricks.com)

2. **Create a Unity Catalog Volume** named `diabetes_raw`:
   - Go to Catalog → workspace → default → Volumes → Create Volume

3. **Upload data files** to the Volume:
   - Upload `data/cdc_brfss_diabetes.csv` and `data/diabetes_hospitals.csv`
   - Target path: `/Volumes/workspace/default/diabetes_raw/`

4. **Import notebooks** into your Databricks workspace:
   - Go to **Workspace** → Create Folder → **Import** each `.py` file from the `notebooks/` folder

5. **Run notebooks in order** (00 → 01 → 02 → 03 → 04 → 05 → 06):
   - Attach a cluster (Databricks Runtime 13.x+ recommended)
   - Run each notebook sequentially

6. **Open the dashboard**:
   - Use SQL queries from `07_dashboard.py` to build the AI/BI Dashboard

---

## Delta Tables Created

### Bronze
- `diabetes_db.bronze_brfss`
- `diabetes_db.bronze_hospitals`

### Silver
- `diabetes_db.silver_brfss`
- `diabetes_db.silver_hospitals`

### Gold (BO1 – Risk Profiling)
- `diabetes_db.gold_risk_by_demographics`
- `diabetes_db.gold_risk_factors_summary`
- `diabetes_db.gold_risk_tier_distribution`
- `diabetes_db.gold_socioeconomic_risk`

### Gold (BO2 – Readmission)
- `diabetes_db.gold_readmission_by_age_race`
- `diabetes_db.gold_readmission_by_medication`
- `diabetes_db.gold_readmission_by_stay`
- `diabetes_db.gold_readmission_drivers`

---

## Live Dashboard

🔗 [View Diabetes Analytics Dashboard](https://dbc-feeb6770-cc53.cloud.databricks.com/dashboardsv3/01f16bea5c5d1b08959cb224b131eeba/published?o=7474658464271415)

> Note: Requires a Databricks account to view.

---

## Testing: Pipeline Update Verification

To verify the pipeline updates automatically when new data is added:

1. Import and run `08_test_new_data.py` — records the **BEFORE** count (High Risk Count = **339**)
2. The notebook inserts **10 new high-risk diabetic patients** into the bronze table
3. Re-run `03_silver_transform_brfss.py`
4. Re-run `05_gold_risk_profiling.py`
5. The High Risk Count rises to **349** — dashboard reflects the change automatically

> Screenshots of the before/after counts are in the `/screenshots` folder.

---

## Submission Checklist

- [ ] Both CSV data files uploaded to DBFS
- [ ] All 8 notebooks imported to Databricks workspace
- [ ] All notebooks run successfully (no errors)
- [ ] All Bronze, Silver, Gold Delta tables exist in `diabetes_db`
- [ ] Databricks SQL Dashboard created with 15 visualisation widgets
- [ ] Screenshots taken of: DBFS file upload, each notebook run, Delta tables, dashboard
- [ ] `prompts.txt` included (AI tool usage log)
- [ ] Submitted via Campusweb before Monday 22.06.2026 at 23:59:59

---

## References

1. Teboul, A. (2021). *Diabetes Health Indicators Dataset*. UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/891/cdc+diabetes+health+indicators

2. Strack, B., DeShazo, J.P., Gennings, C., Olmo, J.L., Ventura, S., Cios, K.J., & Clore, J.N. (2014). Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000 Clinical Database Patient Records. *BioMed Research International*, 2014. https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008
