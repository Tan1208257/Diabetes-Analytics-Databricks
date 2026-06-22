# Databricks notebook source
# MAGIC %md
# MAGIC #Bronze Layer
# MAGIC To ingest Diabetes 130-US Hospitals Data the second Data source
# MAGIC **Source type:** Structured / Database (relational dataset ingested as structured CSV)
# MAGIC **Source:** Diabetes 130-US Hospitals for Years 1999-2008
# MAGIC **Citation:** Strack B. et al. (2014). BioMed Research International. UCI ML Repository ID 296.
# MAGIC https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008

# COMMAND ----------

spark.sql("USE CATALOG workspace")
spark.sql("USE SCHEMA diabetes_db")

RAW_PATH = "/Volumes/workspace/default/diabetes_raw"

# COMMAND ----------

from pyspark.sql import functions as F

hosp_raw = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{RAW_PATH}/diabetes_hospitals.csv")
)

print(f"Rows: {hosp_raw.count()} | Columns: {len(hosp_raw.columns)}")
hosp_raw.printSchema()

# COMMAND ----------

hosp_bronze = (
    hosp_raw
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_source_file",         F.lit("diabetes_hospitals.csv"))
    .withColumn("_source_system",       F.lit("UCI_Hospitals_1999_2008"))
    .withColumn("_layer",               F.lit("bronze"))
)

# COMMAND ----------

(
    hosp_bronze
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("workspace.diabetes_db.bronze_hospitals")
)

print("Bronze table 'workspace.diabetes_db.bronze_hospitals' written successfully.")
spark.sql("SELECT COUNT(*) AS row_count FROM workspace.diabetes_db.bronze_hospitals").show()

# COMMAND ----------

#Performing a Sanity check after writing into the bronze database
spark.sql("""
    SELECT
        readmitted,
        COUNT(*) AS count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM workspace.diabetes_db.bronze_hospitals
    GROUP BY readmitted
    ORDER BY readmitted
""").show()