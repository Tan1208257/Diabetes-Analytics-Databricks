# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer
# MAGIC Business Objective 2 – Hospital Readmission Reduction
# MAGIC
# MAGIC **Goal:** Identify patient and treatment factors that drive 30-day diabetic readmissions.

# COMMAND ----------

spark.sql("USE CATALOG workspace")
spark.sql("USE SCHEMA diabetes_db")

# COMMAND ----------

from pyspark.sql import functions as F

silver = spark.table("workspace.diabetes_db.silver_hospitals")
print(f"Silver Hospitals rows: {silver.count()}")
print(f"30-day readmission rate: {silver.agg(F.round(F.avg('readmitted_30d')*100,2).alias('pct')).collect()[0]['pct']}%")

# COMMAND ----------

#Readmission rate fetched on the basis of race and age
readm_age_race = (
    silver
    .groupBy("age","race")
    .agg(
        F.count("*").alias("patient_count"),
        F.sum("readmitted_30d").alias("readmitted_30d_count"),
        F.round(F.avg("readmitted_30d")*100,2).alias("readmission_30d_rate_pct"),
        F.round(F.avg("any_readmission")*100,2).alias("any_readmission_rate_pct"),
        F.round(F.avg("time_in_hospital"),1).alias("avg_hospital_days"),
        F.round(F.avg("num_medications"),1).alias("avg_medications")
    )
    .filter(F.col("patient_count") >= 10)
    .orderBy(F.desc("readmission_30d_rate_pct"))
)
readm_age_race.show(20)

(
    readm_age_race.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_readmission_by_age_race")
)
print("gold_readmission_by_age_race written.")

# COMMAND ----------

#Impact of insulin while readmitting
readm_medication = (
    silver
    .groupBy("insulin","A1Cresult","diabetesMed")
    .agg(
        F.count("*").alias("patient_count"),
        F.round(F.avg("readmitted_30d")*100,2).alias("readmission_30d_rate_pct"),
        F.round(F.avg("any_readmission")*100,2).alias("any_readmission_rate_pct"),
        F.round(F.avg("time_in_hospital"),1).alias("avg_hospital_days"),
        F.round(F.avg("num_medications"),1).alias("avg_medications")
    )
    .filter(F.col("patient_count") >= 20)
    .orderBy(F.desc("readmission_30d_rate_pct"))
)
readm_medication.show(20)

(
    readm_medication.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_readmission_by_medication")
)
print("gold_readmission_by_medication written.")

# COMMAND ----------

#Readmission on the basis of the length of the patient's stay
readm_stay = (
    silver
    .groupBy("stay_category","any_med_change")
    .agg(
        F.count("*").alias("patient_count"),
        F.round(F.avg("readmitted_30d")*100,2).alias("readmission_30d_rate_pct"),
        F.round(F.avg("total_prior_visits"),2).alias("avg_prior_visits"),
        F.round(F.avg("number_diagnoses"),1).alias("avg_diagnoses"),
        F.round(F.avg("num_medications"),1).alias("avg_medications")
    )
    .orderBy("stay_category",F.desc("readmission_30d_rate_pct"))
)
readm_stay.show(20)

(
    readm_stay.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_readmission_by_stay")
)
print("gold_readmission_by_stay written.")

# COMMAND ----------

#Clinical data on how many patients are readmitted or not
drivers = (
    silver
    .groupBy("readmitted_30d")
    .agg(
        F.count("*").alias("patient_count"),
        F.round(F.avg("time_in_hospital"),2).alias("avg_stay_days"),
        F.round(F.avg("num_medications"),2).alias("avg_medications"),
        F.round(F.avg("num_lab_procedures"),2).alias("avg_lab_procedures"),
        F.round(F.avg("number_diagnoses"),2).alias("avg_diagnoses"),
        F.round(F.avg("total_prior_visits"),2).alias("avg_prior_visits"),
        F.round(F.avg("insulin_used")*100,1).alias("pct_on_insulin"),
        F.round(F.avg("a1c_high")*100,1).alias("pct_high_a1c"),
        F.round(F.avg("any_med_change")*100,1).alias("pct_med_changed"),
        F.round(F.avg("primary_diag_diabetes")*100,1).alias("pct_primary_diag_diabetes")
    )
    .withColumn("readmission_label",
        F.when(F.col("readmitted_30d")==1,"Readmitted <30d").otherwise("Not Readmitted <30d"))
    .orderBy("readmitted_30d")
)
drivers.show()

(
    drivers.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_readmission_drivers")
)
print("All Gold BO2 tables written successfully.")