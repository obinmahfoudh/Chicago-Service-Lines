import pandas as pd
import os    

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load CSV files
service_line = pd.read_csv("./Geocoding_Batches/ExpandedAddressBatches/service_line_info.csv")
assessor = pd.read_csv("Assessor__Archived_05-11-2022__-_Property_Locations_20250225.csv")

# Remove duplicates in service line data
service_line.drop_duplicates(inplace=True)

# Rename property_address to address in assessor
assessor.rename(columns={"property_address": "address"}, inplace=True)
service_line.rename(columns={"Address": "address"}, inplace=True)

# Select relevant columns
assessor_selected = assessor[["address", "property_city", "property_zip", "mailing_address", "mailing_state", "latitude", "longitude", "township_name", "school_elem_district", "school_hs_district"]]

# Merge on address first
merged_on_address = pd.merge(service_line, assessor_selected, on="address", how="inner")
merged_on_address["match_type"] = "address"  # Add match type

# Remove addresses already matched to prevent duplication in mailing_address merge
matched_addresses = set(merged_on_address["address"])
assessor_filtered = assessor_selected[~assessor_selected["mailing_address"].isin(matched_addresses)]

# Merge on mailing_address
merged_on_mailing = pd.merge(service_line, assessor_filtered, left_on="address", right_on="mailing_address", how="inner")
merged_on_mailing["match_type"] = "mailing_address"

# Combine both matches
merged_combined = pd.concat([merged_on_address, merged_on_mailing])

# Create a single 'matched_address' column where we take the property address if available, otherwise the mailing address
merged_combined["matched_address"] = merged_combined["address"].combine_first(merged_combined["mailing_address"])

# Keep only relevant columns (dropping duplicate address columns)
merged_combined = merged_combined[["matched_address", "match_type", "property_city", "property_zip", "latitude", "longitude", "township_name", "school_elem_district", "school_hs_district","Private Service Line Material", "Public Service Line Material"]]

# Drop duplicate rows
merged_matched = merged_combined.drop_duplicates()

# Save the final merged dataset
merged_matched.to_csv("./ExpandedStuff/matched_addresses.csv", index=False)

# Print summary
print(f"Total matched addresses saved: {len(merged_matched)}")
