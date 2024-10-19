import plotly.express as px

# Relative imports
from . import data_path, output_path, read_data

df = read_data(data_path / "Data_Insights_Synthetic_Dataset.csv")

# Sum all relevant charge columns to get the total charges per DRG
df["TotalCharges"] = df[["PharmacyCharge", "AccommodationCharge", "CCU_Charges", "ICU_Charge", "TheatreCharge", 
                         "ProsthesisCharge", "OtherCharges", "BundledCharges"]].sum(axis=1)

drg_charges = df.groupby("AR-DRG")["TotalCharges"].agg(["sum", "max"]).reset_index()

# Visualize with Plotly
for agg in ["sum", "max"]:
    fig = px.bar(drg_charges, x="AR-DRG", y=f"{agg}", 
                title=f"{agg} Charges by DRG", 
                labels={
                    "AR-DRG": "DRG", 
                    "TotalCharges": "Total Charges"
                    })
    fig.write_html(output_path / f"{agg}_Charges_by_DRG.html", include_plotlyjs="cdn")
