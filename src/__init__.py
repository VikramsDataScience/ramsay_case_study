from pathlib import Path
from .config import Config
from typing import Optional
import pandas as pd

# Model version
__version__ = 0.01

# Load storage paths from the config.py file
config = Config()
case_study_path = Path(config.case_study_path)
data_path = Path(config.data_path)
numerical_cols = config.numerical_cols
categorical_cols = config.categorical_cols
charge_cols = config.charge_cols

def read_data(df_path, 
            sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Read either XLSX or CSV file.
    _sheet_name_ arg is optional and is only required for an XLSX file.
    """

    if ".xlsx" in df_path.suffix:
        df = pd.read_excel(df_path, sheet_name)
    elif ".csv" in df_path.suffix:
        df = pd.read_csv(df_path)

    return df
