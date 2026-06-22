# Databricks notebook source
# MAGIC %md
# MAGIC #Test: Add New Data & Verify Dashboard Updates
# MAGIC
# MAGIC **Purpose:** Demonstrates that adding new data to a source table
# MAGIC automatically updates the dashboard when the pipeline is re-run.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. Run Cell 1 – record BEFORE counts
# MAGIC 2. Run Cell 2 – insert 10 new high-risk diabetic patients
# MAGIC 3. Re-run notebook 03 (Silver BRFSS)
# MAGIC 4. Re-run notebook 05 (Gold Risk Profiling)
# MAGIC 5. Run Cell 3 – record AFTER counts → dashboard reflects change

# COMMAND ----------

# MAGIC %md
# MAGIC ## BEFORE counts

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     COUNT(*) AS total_patients,
# MAGIC     SUM(CASE WHEN risk_tier = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
# MAGIC     ROUND(AVG(Diabetes_binary) * 100, 1) AS diabetes_prevalence_pct
# MAGIC FROM diabetes_db.silver_brfss;

# COMMAND ----------

# MAGIC %md
# MAGIC ##Inserting 10 new high-risk diabetic patients into Bronze table

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO diabetes_db.bronze_brfss
# MAGIC     (Diabetes_binary, HighBP, HighChol, CholCheck, BMI, Smoker, Stroke,
# MAGIC      HeartDiseaseorAttack, PhysActivity, Fruits, Veggies, HvyAlcoholConsump,
# MAGIC      AnyHealthcare, NoDocbcCost, GenHlth, MentHlth, PhysHlth, DiffWalk,
# MAGIC      Sex, Age, Education, Income,
# MAGIC      _ingestion_timestamp, _source_file, _source_system, _layer)
# MAGIC VALUES
# MAGIC     (1, 1, 1, 1, 38.5, 1, 1, 1, 0, 0, 0, 0, 1, 0, 5, 20, 25, 1, 1, 10, 3, 2, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 41.2, 1, 0, 1, 0, 0, 1, 0, 1, 0, 4, 15, 20, 1, 0, 11, 2, 1, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 36.8, 1, 1, 1, 0, 0, 0, 0, 1, 1, 5, 25, 28, 1, 1, 9,  3, 2, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 44.0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 5, 18, 22, 1, 0, 12, 2, 1, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 39.5, 1, 0, 1, 0, 0, 1, 0, 1, 0, 4, 10, 18, 1, 1, 10, 3, 2, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 42.3, 1, 1, 1, 0, 0, 0, 0, 1, 1, 5, 22, 26, 1, 0, 11, 2, 2, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 37.1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 4, 14, 20, 1, 1, 9,  3, 1, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 45.6, 1, 1, 1, 0, 0, 1, 0, 1, 0, 5, 20, 24, 1, 0, 12, 2, 2, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 40.8, 0, 1, 1, 0, 0, 0, 0, 1, 1, 5, 16, 21, 1, 1, 10, 3, 1, current_timestamp(), 'test_data', 'manual_insert', 'bronze'),
# MAGIC     (1, 1, 1, 1, 43.2, 1, 0, 1, 0, 1, 0, 0, 1, 0, 4, 12, 19, 1, 0, 11, 2, 2, current_timestamp(), 'test_data', 'manual_insert', 'bronze');

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC 1. Run **03_silver_transform_brfss** (re-processes bronze → silver)
# MAGIC 2. Run **05_gold_risk_profiling** (re-processes silver → gold)

# COMMAND ----------

# MAGIC %md
# MAGIC ## AFTER counts 

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     COUNT(*) AS total_patients,
# MAGIC     SUM(CASE WHEN risk_tier = 'High' THEN 1 ELSE 0 END) AS high_risk_count,
# MAGIC     ROUND(AVG(Diabetes_binary) * 100, 1) AS diabetes_prevalence_pct
# MAGIC FROM diabetes_db.silver_brfss;