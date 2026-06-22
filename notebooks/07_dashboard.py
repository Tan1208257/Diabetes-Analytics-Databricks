# Databricks notebook source
# MAGIC %md
# MAGIC # Dashboard Queries
# MAGIC
# MAGIC This notebook contains all SQL queries powering the **DIABETES ANALYTICS DASHBOARD**.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # BUSINESS OBJECTIVE 1: Population Risk Profiling
# MAGIC **Goal:** Identify demographic and lifestyle segments with highest diabetes prevalence.
# MAGIC ---

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 1 – High Risk Count (Counter)
# MAGIC **Dataset name:** `high_risk_count`
# MAGIC **Visualisation:** Counter | **Title:** High Risk Count
# MAGIC **Value field:** `High Risk Individuals`

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS `High Risk Individuals`
# MAGIC FROM diabetes_db.silver_brfss
# MAGIC WHERE risk_tier = 'High';

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 2 – Avg Risk Score (Counter)
# MAGIC **Dataset name:** `avg_risk_score_high`
# MAGIC **Visualisation:** Counter | **Title:** Avg Risk Score
# MAGIC **Value field:** `Avg Risk Score (High-Risk)`

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(AVG(risk_score), 1) AS `Avg Risk Score (High-Risk)`
# MAGIC FROM diabetes_db.silver_brfss
# MAGIC WHERE risk_tier = 'High';

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 3 – Diabetes Prevalence by Age Group (Bar Chart)
# MAGIC **Dataset name:** `diabetes_prevalence_by_age`
# MAGIC **Visualisation:** Bar Chart | **Title:** Diabetes Prevalence by Age
# MAGIC **X-axis:** `age_group` | **Y-axis:** `diabetes_prevalence_pct`

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     age_group,
# MAGIC     ROUND(AVG(Diabetes_binary) * 100, 1) AS diabetes_prevalence_pct,
# MAGIC     COUNT(*)                              AS population
# MAGIC FROM diabetes_db.silver_brfss
# MAGIC GROUP BY age_group
# MAGIC ORDER BY age_group;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 4 – Risk Score by BMI Category (Grouped Bar Chart)
# MAGIC **Dataset name:** `risk_score_by_bmi`
# MAGIC **Visualisation:** Bar Chart (Grouped) | **Title:** Risk Score by BMI Category
# MAGIC **X-axis:** `bmi_category` | **Y-axis:** `avg_risk_score` | **Group by:** `diabetes_label`
# MAGIC **Legend:** Diabetic (red) / No Diabetes (green)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     bmi_category,
# MAGIC     diabetes_label,
# MAGIC     ROUND(AVG(risk_score), 2) AS avg_risk_score,
# MAGIC     COUNT(*)                  AS population
# MAGIC FROM diabetes_db.silver_brfss
# MAGIC GROUP BY bmi_category, diabetes_label
# MAGIC ORDER BY bmi_category, diabetes_label;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 5 – Risk Tier Distribution (Donut / Pie Chart)
# MAGIC **Dataset name:** `risk_tier_pie`
# MAGIC **Visualisation:** Pie Chart | **Title:** Risk Tier Distribution
# MAGIC **Label:** `risk_tier` | **Value:** `population` | **Color:** `risk_tier`
# MAGIC **Legend:** Medium (yellow) / Low (green) / High (red)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     risk_tier,
# MAGIC     COUNT(*) AS population
# MAGIC FROM diabetes_db.silver_brfss
# MAGIC GROUP BY risk_tier
# MAGIC ORDER BY population DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC # BUSINESS OBJECTIVE 2: Hospital Readmission Reduction
# MAGIC **Goal:** Identify patient and treatment factors that drive 30-day diabetic readmissions.
# MAGIC ---

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 6 – 30-Day Readmission Rate (Counter)
# MAGIC **Dataset name:** `readmission_rate`
# MAGIC **Visualisation:** Counter | **Title:** Readmission %
# MAGIC **Value field:** `30-Day Readmission Rate (%)`

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(AVG(readmitted_30d) * 100, 1) AS `30-Day Readmission Rate (%)`
# MAGIC FROM diabetes_db.silver_hospitals;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 7 – Avg Hospital Stay (Counter)
# MAGIC **Dataset name:** `avg_hospital_stay`
# MAGIC **Visualisation:** Counter | **Title:** Avg Hosp Stay
# MAGIC **Value field:** `Avg Hospital Stay (Days)`

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ROUND(AVG(time_in_hospital), 1) AS `Avg Hospital Stay (Days)`
# MAGIC FROM diabetes_db.silver_hospitals;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Widget 8 – Readmission Rate by Age Group (Line Chart)
# MAGIC **Dataset name:** `readmission_by_age`
# MAGIC **Visualisation:** Line Chart | **Title:** Readmission Rate by Age Group
# MAGIC **X-axis:** `age` | **Y-axis:** `readmission_30d_rate_pct`

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     age,
# MAGIC     ROUND(AVG(readmitted_30d) * 100, 1) AS readmission_30d_rate_pct,
# MAGIC     COUNT(*) AS patient_count
# MAGIC FROM diabetes_db.silver_hospitals
# MAGIC GROUP BY age
# MAGIC ORDER BY age;