# Databricks notebook source
# MAGIC %md
# MAGIC **Diabetes Analytics Platform** 
# MAGIC
# MAGIC **Data Sources:**
# MAGIC - DataSource 1 (Object/CSV): CDC BRFSS 2015 Diabetes Health Indicators – UCI ML Repo ID 891
# MAGIC - DataSource 2 (Structured/DB): Diabetes 130-US Hospitals 1999-2008 – UCI ML Repo ID 296
# MAGIC
# MAGIC **Business Objectives:**
# MAGIC The business objectives created by me based on the datasets chosen are:
# MAGIC 1. Population Risk Profiling – identify high-risk demographic/lifestyle segments
# MAGIC 2. Hospital Readmission Reduction – detect drivers of 30-day diabetic readmissions

# COMMAND ----------

# MAGIC %md
# MAGIC Both CSV files are in: `/Volumes/workspace/default/diabetes_raw/`

# COMMAND ----------

#Created a schema using spark sql
spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.diabetes_db COMMENT 'Diabetes Analytics'")
spark.sql("USE CATALOG workspace")
spark.sql("USE SCHEMA diabetes_db")
print("Schema 'workspace.diabetes_db' ready.")

# COMMAND ----------

#To verify the datasource path
RAW_PATH = "/Volumes/workspace/default/diabetes_raw"
files = dbutils.fs.ls(RAW_PATH)
for f in files:
    print(f.name, f.size, "bytes")