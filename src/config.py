class Config:
    def __init__(self):
        self.case_study_path = "/app"
        self.data_path = "/app/data"
        self.numerical_cols = ["CCU_Charges", "ICU_Charge", "TheatreCharge", "ProsthesisCharge", "OtherCharges", "BundledCharges", "UnplannedTheatreVisit", "InfantWeight", "Readmission28Days", "HoursMechVentilation", "PalliativeCareStatus", "PharmacyCharge"]
        self.categorical_cols = ["UnplannedTheatreVisit", "Readmission28Days", "PalliativeCareStatus"]
        self.charge_cols = ["PharmacyCharge", "AccommodationCharge", "CCU_Charges", "ICU_Charge"]
        