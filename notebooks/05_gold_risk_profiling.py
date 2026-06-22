# Databricks notebook source
# MAGIC %md
# MAGIC # Gold Layer
# MAGIC Business Objective 1 – Population Risk Profiling
# MAGIC
# MAGIC **Goal:** Identify demographic and lifestyle segments with highest diabetes prevalence to support preventive care targeting.

# COMMAND ----------

spark.sql("USE CATALOG workspace")
spark.sql("USE SCHEMA diabetes_db")

# COMMAND ----------

from pyspark.sql import functions as F

silver = spark.table("workspace.diabetes_db.silver_brfss")
print(f"Silver BRFSS rows: {silver.count()}")

# COMMAND ----------

#Diabetes prevalence by age, gender, BMI
risk_demographics = (
    silver
    .groupBy("age_group","gender","bmi_category")
    .agg(
        F.count("*").alias("total_population"),
        F.sum("Diabetes_binary").alias("diabetic_count"),
        F.round(F.avg("Diabetes_binary")*100,2).alias("diabetes_prevalence_pct"),
        F.round(F.avg("risk_score"),2).alias("avg_risk_score"),
        F.round(F.avg("BMI"),1).alias("avg_bmi"),
        F.round(F.avg("GenHlth"),2).alias("avg_general_health")
    )
    .orderBy(F.desc("diabetes_prevalence_pct"))
)
risk_demographics.show(20)

(
    risk_demographics.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_risk_by_demographics")
)
print("gold_risk_by_demographics written.")

# COMMAND ----------

from functools import reduce
from pyspark.sql import DataFrame

factors = [
    ("HighBP","High Blood Pressure"),("HighChol","High Cholesterol"),
    ("Smoker","Smoker"),("HeartDiseaseorAttack","Heart Disease/Attack"),
    ("Stroke","Stroke History"),("DiffWalk","Difficulty Walking"),
]

def factor_prevalence(df, col_name, label):
    return df.filter(F.col(col_name)==1).agg(
        F.lit(label).alias("risk_factor"),
        F.count("*").alias("affected_population"),
        F.round(F.avg("Diabetes_binary")*100,2).alias("diabetes_prevalence_pct"),
        F.round(F.avg("risk_score"),2).alias("avg_risk_score")
    )

frames = [factor_prevalence(silver, c, l) for c, l in factors]
risk_factors_summary = reduce(DataFrame.unionAll, frames)
risk_factors_summary.show()

(
    risk_factors_summary.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_risk_factors_summary")
)
print("gold_risk_factors_summary written.")

# COMMAND ----------

#Risk tier being created to generate a pie chart for dashboard
risk_tier_dist = (
    silver
    .groupBy("risk_tier","diabetes_label","income_label")
    .agg(
        F.count("*").alias("population"),
        F.round(F.avg("BMI"),1).alias("avg_bmi"),
        F.round(F.avg("GenHlth"),2).alias("avg_gen_health"),
        F.round(F.avg("PhysHlth"),1).alias("avg_unhealthy_days")
    )
    .orderBy("risk_tier","diabetes_label")
)
risk_tier_dist.show(30)

(
    risk_tier_dist.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_risk_tier_distribution")
)

# COMMAND ----------

#Socioeconomic effects of diabetes being fetched
socioeconomic = (
    silver
    .groupBy("income_label","education_label")
    .agg(
        F.count("*").alias("population"),
        F.round(F.avg("Diabetes_binary")*100,2).alias("diabetes_prevalence_pct"),
        F.round(F.avg("BMI"),1).alias("avg_bmi"),
        F.round(F.avg("risk_score"),2).alias("avg_risk_score")
    )
    .orderBy(F.desc("diabetes_prevalence_pct"))
)
socioeconomic.show(20)

(
    socioeconomic.write.format("delta").mode("overwrite")
    .option("overwriteSchema","true")
    .saveAsTable("workspace.diabetes_db.gold_socioeconomic_risk")
)
print("All Gold BO1 tables written successfully.")