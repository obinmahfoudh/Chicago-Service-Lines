## Merges service line data with matches assessor data
## Checks for matches in address and mailing_address column
## Saves a csv with matched data
## Saves a csvs for duplicate rows from address, mailing_address and service line address

import pandas as pd
import os    


os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load CSV files
geocode_data = pd.read_csv("./AssessorGeocodeBatches/Merged.csv")
assessor = pd.read_csv("../Assessor__Archived_05-11-2022__-_Property_Locations_20250225.csv")

print(f"Number of duplicates in geocode_data: {geocode_data['Address'].duplicated().sum()}")
print(f"Number of duplicates in assessor: {assessor['property_address'].duplicated().sum()}")

geocode_data = geocode_data.drop_duplicates(subset=["Address"])
assessor = assessor.drop_duplicates(subset=["property_address"])

geocode_data["Address"] = geocode_data["Address"].str.replace(r",\s*Chicago,\s*IL\s*,?\s*$", "", regex=True)


assessor_selected = assessor[[
    "property_address", "property_city", "property_zip", "mailing_address",
    "mailing_state", "township_name",
    "school_elem_district", "school_hs_district"
]]

# Merge the datasets on 'property_address' from the assessor dataset and 'Address' from geocode dataset
merged_data = geocode_data.merge(assessor_selected, left_on="Address", right_on="property_address", how="left")

# Save the merged dataset
merged_data.to_csv("merged_assessor_geocode_data.csv", index=False)

print("Merging complete! File saved as merged_assessor_geocode_data.csv")

