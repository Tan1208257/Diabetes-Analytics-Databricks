# Databricks notebook source
# MAGIC %md
# MAGIC #Silver Layer
# MAGIC To clean & transform BRFSS Data

# COMMAND ----------

spark.sql("USE CATALOG workspace")
spark.sql("USE SCHEMA diabetes_db")

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, DoubleType

brfss_bronze = spark.table("workspace.diabetes_db.bronze_brfss")
print(f"Bronze row count: {brfss_bronze.count()}")

# COMMAND ----------

age_labels = {1:"18-24",2:"25-29",3:"30-34",4:"35-39",5:"40-44",
              6:"45-49",7:"50-54",8:"55-59",9:"60-64",10:"65-69",
              11:"70-74",12:"75-79",13:"80+"}
age_map_expr = F.create_map([F.lit(x) for pair in age_labels.items() for x in pair])

education_labels = {1:"Never attended",2:"Elementary",3:"Some high school",
                    4:"High school grad",5:"Some college",6:"College grad"}
edu_map_expr = F.create_map([F.lit(x) for pair in education_labels.items() for x in pair])

income_labels = {1:"<$10k",2:"$10-15k",3:"$15-20k",4:"$20-25k",
                 5:"$25-35k",6:"$35-50k",7:"$50-75k",8:">$75k"}
inc_map_expr = F.create_map([F.lit(x) for pair in income_labels.items() for x in pair])

brfss_silver = (
    brfss_bronze
    .withColumn("BMI",             F.col("BMI").cast(DoubleType()))
    .withColumn("MentHlth",        F.col("MentHlth").cast(IntegerType()))
    .withColumn("PhysHlth",        F.col("PhysHlth").cast(IntegerType()))
    .withColumn("Age",             F.col("Age").cast(IntegerType()))
    .withColumn("age_group",       age_map_expr[F.col("Age")])
    .withColumn("education_label", edu_map_expr[F.col("Education")])
    .withColumn("income_label",    inc_map_expr[F.col("Income")])
    .withColumn("gender",          F.when(F.col("Sex")==1,"Male").otherwise("Female"))
    .withColumn("bmi_category",
        F.when(F.col("BMI") < 18.5, "Underweight")
         .when(F.col("BMI") < 25.0, "Normal")
         .when(F.col("BMI") < 30.0, "Overweight")
         .otherwise("Obese"))
    .withColumn("diabetes_label",
        F.when(F.col("Diabetes_binary")==0,"No Diabetes").otherwise("Diabetic"))
    .withColumn("risk_score",
        F.col("HighBP").cast(IntegerType()) +
        F.col("HighChol").cast(IntegerType()) +
        F.col("Smoker").cast(IntegerType()) +
        F.col("HeartDiseaseorAttack").cast(IntegerType()) +
        F.col("Stroke").cast(IntegerType()) +
        F.col("DiffWalk").cast(IntegerType()) +
        F.when(F.col("PhysActivity")==0,1).otherwise(0))
    .withColumn("risk_tier",
        F.when(F.col("risk_score") <= 1,"Low")
         .when(F.col("risk_score") <= 3,"Medium")
         .otherwise("High"))
    .drop("_ingestion_timestamp","_source_file","_source_system","_layer")
    .withColumn("_silver_timestamp", F.current_timestamp())
    .withColumn("_layer", F.lit("silver"))
)

# COMMAND ----------

#Writing into the silver database 
(
    brfss_silver
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("workspace.diabetes_db.silver_brfss")
)

print("Silver table 'workspace.diabetes_db.silver_brfss' written successfully.")
spark.sql("SELECT COUNT(*) AS rows FROM workspace.diabetes_db.silver_brfss").show()

# COMMAND ----------

spark.sql("""
    SELECT diabetes_label, bmi_category, risk_tier, COUNT(*) AS cnt
    FROM workspace.diabetes_db.silver_brfss
    GROUP BY diabetes_label, bmi_category, risk_tier
    ORDER BY diabetes_label, cnt DESC
""").show(30)