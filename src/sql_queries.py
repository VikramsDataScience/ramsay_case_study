from sqlalchemy import create_engine
import pandas as pd

# Relative imports
from . import data_path

sql_engine = create_engine("sqlite:///ramsay_db.db")
connection = sql_engine.connect()
df = pd.read_csv(data_path / "Data_Insights_Synthetic_Dataset.csv")

# Write the dataframe to the SQLite database
df.to_sql('admissions_table', con=connection, if_exists='replace', index=False)

# SQL query for total and average admissions per month
average_admissions_query = """
SELECT 
    strftime('%Y-%m', AdmissionDate) AS MonthYear,
    COUNT(episode_id) AS TotalAdmissions,
    ROUND(AVG(AdmissionCount) OVER(), 0) AS AverageAdmissions
FROM (
    SELECT 
        episode_id, 
        AdmissionDate,
        COUNT(episode_id) OVER (PARTITION BY strftime('%Y-%m', AdmissionDate)) AS AdmissionCount
    FROM admissions_table
    WHERE AdmissionDate >= date('now', '-2 years')
)
GROUP BY MonthYear
ORDER BY MonthYear ASC;
"""

# Execute the query and load the result into a pandas DataFrame
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
percentiles = df_charges.groupby(['PrincipalDiagnosis', 'Sex'])['TotalCharges'].quantile([0.25, 0.50, 0.75, 0.90]).unstack()

# Calculate the average charge
average_charge = df_charges.groupby(['PrincipalDiagnosis', 'Sex'])['TotalCharges'].mean()

# Combine the percentiles and average charge into a single DataFrame
df_percentiles = pd.concat([percentiles, average_charge], axis=1)
df_percentiles.columns = ['25th Percentile', '50th Percentile', '75th Percentile', '90th Percentile', 'AverageCharge']

# Save the result to a CSV file
# df_percentiles.to_csv(data_path / "Total_Charges_by_Diagnosis.csv", index=False)

# Display the result
print(df_percentiles)
