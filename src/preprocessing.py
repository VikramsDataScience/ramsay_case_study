import pandas as pd
import numpy as np
import os
import sys
import contextlib
from missforest.missforest import MissForest

# Relative imports
from . import data_path, categorical_cols, numerical_cols, charge_cols, read_data

def read_impute_data(df,
                    float_cols,
                    categoricals,
                    output_path) -> pd.DataFrame:
    """Perform dynamic imputation with Missing Forest."""

    missforest_imputer = MissForest()
    df_copy = df.copy()
    print("Selected float columns for imputation:", float_cols)
    print("Shape of df[float_cols]:", df[float_cols].shape)
    print(df[float_cols])
    # Perform imputation only on the specified float_cols
    with suppress_stdout():
        imputed_values = missforest_imputer.transform(x=df[float_cols]),
                                                            #categorical=categoricals)
    
    # Create a DataFrame from the imputed values and ensure column names are preserved
    imputed_df = pd.DataFrame(imputed_values, columns=float_cols, index=df.index)

    # Update only the imputed columns in the original DataFrame
    df_copy[float_cols] = imputed_df[float_cols]
    
    # Verify if there are any NaNs and verify dtypes in the DF
    print("NaN values:\n", df_copy.isna().sum())
    print("Data types:\n", df_copy.dtypes)
    
    # Save the entire DataFrame, including imputed and non-imputed columns, to CSV
    df_copy.to_csv(output_path, index=False)  
    
    return df_copy


@contextlib.contextmanager
def suppress_stdout():
    """For any library that contains (undesirably) verbose output, use this boilerplate function to suppress
    that output in the CLI.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


df = read_data(df_path = data_path / "Data_Insights_Synthetic_Dataset.xlsx",
                sheet_name = "Data Insights - Synthetic Datas")

def clean_clinical_charges(value):
    """Clean up the erroneous values in the charge columns"""

    # Check if the value is in string form and contains "e+" (scientific notation)
    if isinstance(value, str) and "e+" in value:
        # Split the string at "e+" and keep the base value
        base_value = value.split("e+")[0]
        base_value = float(base_value)
    else:
        # For other values, convert to float directly
        try:
            base_value = float(value)
        except ValueError:
            # If conversion fails, return NaN
            return np.nan
    
    # Handle negative values by converting them to positive
    if base_value < 0:
        base_value = abs(base_value)
    
    # Set a maximum value to remove extremely large numbers
    if base_value > 1000:
        return np.nan
    
    # Multiply valid values by 100 and return (i.e. emulate a cents to dollars conversion)
    return base_value * 100


# Apply the function to all the charge columns
for col in charge_cols:
    df[col] = df[col].astype(str).apply(clean_clinical_charges)

# Impute the binary categorical cols with a new category called "unknown"
df = df.fillna({"UnplannedTheatreVisit": "unknown", 
                "Readmission28Days": "unknown", 
                "PalliativeCareStatus": "unknown"})

# Convert "AdmissionTime" and "SeparationTime" cols to 24 hour formatted clock
df["AdmissionTime"] = pd.to_datetime(df["AdmissionTime"], format="%H:%M:%S").dt.time
df["SeparationTime"] = pd.to_datetime(df["SeparationTime"], format="%H:%M:%S").dt.time

# Create a new Feature: Length of Stay (LOS)
df["AdmissionDate"] = pd.to_datetime(df["AdmissionDate"])
df["SeparationDate"] = pd.to_datetime(df["SeparationDate"])
df["LengthOfStay"] = (df["SeparationDate"] - df["AdmissionDate"]).dt.days

# Perform imputation, convert to CSV and save for downstream consumption
df = read_impute_data(df=df,
                      float_cols=numerical_cols,
                      categoricals=categorical_cols,
                      output_path = data_path / "Data_Insights_Synthetic_Dataset.csv")
