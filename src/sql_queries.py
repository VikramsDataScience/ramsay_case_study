from sqlalchemy import create_engine
import pandas as pd

# Relative imports
from . import data_path

sql_engine = create_engine("sqlite:///ramsay_db.db")
connection = sql_engine.connect()
df = pd.read_csv(data_path / "Data_Insights_Synthetic_Dataset.csv")

# Write the dataframe to the SQLite database
df.to_sql("admissions_table", con=connection, if_exists="replace", index=False)

# SQL query for total and average admissions per month
average_admissions_query = """
WITH MonthlyAdmissions AS (
    SELECT 
        strftime("%Y-%m", AdmissionDate) AS MonthYear,
        COUNT(episode_id) AS TotalAdmissions
    FROM admissions_table
    WHERE AdmissionDate >= date("now", "-3 years")  -- Extend to 3 years to have enough data for the first year"s average
    GROUP BY MonthYear
),
MovingAverage AS (
    SELECT 
        MonthYear,
        TotalAdmissions,
        AVG(TotalAdmissions) OVER (
            ORDER BY MonthYear
            ROWS BETWEEN 1 PRECEDING AND CURRENT ROW -- Calculate Moving Average between current month and the one preceding
        ) AS AverageAdmissions,
        ROW_NUMBER() OVER (ORDER BY MonthYear) AS RowNum
    FROM MonthlyAdmissions
)
SELECT 
    MonthYear,
    TotalAdmissions,
    ROUND(AverageAdmissions, 0) AS AverageAdmissions
FROM MovingAverage
WHERE RowNum > 0  -- Show results for the last 2 years (24 months)
ORDER BY MonthYear ASC;
"""

# Execute the query and load the result into a pandas DataFrame and save to storage as CSV
df_admissions = pd.read_sql(average_admissions_query, connection)
df_admissions.to_csv(data_path / "Total_Average_Admissions.csv", index=False)

# SQL query for distribution of Total Charges by PrincipalDiagnosis and Sex
total_charges_query = """
WITH Charges AS (
    SELECT 
        episode_id,
        PrincipalDiagnosis,
        Sex,
        (AccommodationCharge + CCU_Charges + ICU_Charge + TheatreCharge + 
        PharmacyCharge + ProsthesisCharge + OtherCharges + BundledCharges) AS TotalCharges
    FROM admissions_table
)
SELECT 
    PrincipalDiagnosis,
    Sex,
    TotalCharges
FROM Charges
ORDER BY PrincipalDiagnosis, Sex;
"""

# Fetch the data from the database
df_charges = pd.read_sql(total_charges_query, connection)

# Calculate percentiles
percentiles = df_charges.groupby(["PrincipalDiagnosis", "Sex"])["TotalCharges"].quantile([0.25, 0.50, 0.75, 1]).unstack()

# Calculate the average charge
average_charge = df_charges.groupby(["PrincipalDiagnosis", "Sex"])["TotalCharges"].mean()

# Combine the percentiles and average charge into a single DataFrame
df_percentiles = pd.concat([percentiles, average_charge], axis=1)
df_percentiles.columns = ["25th Percentile", "50th Percentile", "75th Percentile", "Maximum", "AverageCharge"]

# Save the result to a CSV file
df_percentiles.reset_index().to_csv(data_path / "Percentile_Charges_by_Diagnosis_Sex.csv", index=False)
