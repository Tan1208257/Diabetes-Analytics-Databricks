# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer
# MAGIC Clean & Transform Hospital Data

# COMMAND ----------

spark.sql("USE CATALOG workspace")
spark.sql("USE SCHEMA diabetes_db")

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType

hosp_bronze = spark.table("workspace.diabetes_db.bronze_hospitals")
print(f"Bronze row count: {hosp_bronze.count()}")

# COMMAND ----------

# Since meaningless values like were found in the data source, replacing them with a standard "null" value
all_str_cols = [f.name for f in hosp_bronze.schema.fields if isinstance(f.dataType, StringType)]
print(f"String columns to clean: {all_str_cols}")

hosp_clean = hosp_bronze
for c in all_str_cols:
    hosp_clean = hosp_clean.withColumn(c, F.when(F.col(c) == "?", None).otherwise(F.col(c)))

# COMMAND ----------

int_cols = ["time_in_hospital","num_lab_procedures","num_procedures",
            "num_medications","number_outpatient","number_emergency",
            "number_inpatient","number_diagnoses","admission_type_id",
            "discharge_disposition_id","admission_source_id"]

for c in int_cols:
    hosp_clean = hosp_clean.withColumn(c, F.expr(f"try_cast(`{c}` AS INT)"))

# COMMAND ----------

hosp_silver = (
    hosp_clean
    .withColumn("readmitted_30d",
        F.when(F.col("readmitted")=="<30",1).otherwise(0).cast(IntegerType()))
    .withColumn("any_readmission",
        F.when(F.col("readmitted")=="NO",0).otherwise(1).cast(IntegerType()))
    .withColumn("primary_diag_diabetes",
        F.when(F.col("diag_1").startswith("250"),1).otherwise(0).cast(IntegerType()))
    .withColumn("age_midpoint",
        F.expr("try_cast(regexp_extract(age, '\\\\[(\\\\d+)-', 1) AS INT)") + 5)
    .withColumn("any_med_change",
        F.when(F.col("change")=="Ch",1).otherwise(0).cast(IntegerType()))
    .withColumn("total_prior_visits",
        F.coalesce(F.col("number_outpatient"),F.lit(0)) +
        F.coalesce(F.col("number_emergency"),F.lit(0)) +
        F.coalesce(F.col("number_inpatient"),F.lit(0)))
    .withColumn("stay_category",
        F.when(F.col("time_in_hospital") <= 2,"Short (1-2d)")
         .when(F.col("time_in_hospital") <= 5,"Medium (3-5d)")
         .when(F.col("time_in_hospital") <= 9,"Long (6-9d)")
         .otherwise("Extended (10+d)"))
    .withColumn("insulin_used",
        F.when(F.col("insulin")=="No",0).otherwise(1).cast(IntegerType()))
    .withColumn("a1c_high",
        F.when(F.col("A1Cresult").isin([">7",">8"]),1).otherwise(0).cast(IntegerType()))
    .drop("_ingestion_timestamp","_source_file","_source_system","_layer")
    .withColumn("_silver_timestamp", F.current_timestamp())
    .withColumn("_layer", F.lit("silver"))
)

# COMMAND ----------

#Removing duplicate values and writing into the silver table
hosp_silver = hosp_silver.dropDuplicates(["encounter_id"])
print(f"Rows after dedup: {hosp_silver.count()}")

(
    hosp_silver
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("workspace.diabetes_db.silver_hospitals")
)

print("Silver table 'workspace.diabetes_db.silver_hospitals' written successfully.")

# COMMAND ----------

spark.sql("""
    SELECT readmitted, readmitted_30d, COUNT(*) AS cnt
    FROM workspace.diabetes_db.silver_hospitals
    GROUP BY readmitted, readmitted_30d
    ORDER BY readmitted
""").show()