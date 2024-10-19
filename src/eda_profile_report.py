from os.path import exists
from ydata_profiling import ProfileReport

# Relative imports
from . import output_path, data_path, read_data

df = read_data(df_path = data_path / "Data_Insights_Synthetic_Dataset.xlsx",
                sheet_name = "Data Insights - Synthetic Datas")

# Generate ydata profile report and export to storage as an HTML document
if not exists(output_path / "Ramsay_EDA_Profile_Report.html"):
    profile_report = ProfileReport(df,
                                title="Ramsay Case Study EDA Report",
                                tsmode=False, # Since the data is not a Time Series deactivate the "tsmode"
                                explorative=True)

    profile_report.to_file(output_path / "Ramsay_EDA_Profile_Report.html")
