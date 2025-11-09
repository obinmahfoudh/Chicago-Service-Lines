## Merges service line data with matches assessor data
## Checks for matches in address and mailing_address column
## Saves a csv with matched data
## Saves a csvs for duplicate rows from address, mailing_address and service line address

import pandas as pd
import os    


os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load CSV files
service_line = pd.read_csv("./service_line_info.csv")
assessor = pd.read_csv("Cook_County_Address_Points_20250325.csv", low_memory=False)

# Some addresses recorded as Galvanized also have a duplicate record stating not lead
# To prevent matching each address unit to multiple records of same service line we will remove duplicates
# Keeping last match since the galvanized information seems to be at bottom but should probably clean data better
#service_line.drop_duplicates(subset=["Address"], keep= "last")


# Rename property_address to address in assessor
assessor.rename(columns={"CMPADDABRV": "address"}, inplace=True)
service_line.rename(columns={"Address": "address"}, inplace=True)


# Select columns we want to merge
assessor_selected = assessor[["address", "geocode_muni", "Post_Code", "Lat", "Long", "TWP_NAME"]]

# Merge on address
merged_combined = pd.merge(service_line, assessor_selected, on="address", how="inner")

# Count duplicate matches by address
# Looking through duplicates are caused by:
# Assessor: Duplicated due to units within an apartment. (Same address has different value in property_apt_no column)
# Service Line: Seems to have multiple records of same address if address uses galvanized service line. One stating not lead and another stating its galvanized
duplicate_count = merged_combined.duplicated(subset=["address"], keep=False).sum()

# Drop duplicates to get the final merged dataset
# Only drops rows that are completely similar (all columns), so multiple rows might still appear for same address based on conditions above
# From tests it looks like 
merged_matched = merged_combined.drop_duplicates()

# Perform a left merge to keep all service line addresses, even those without matches
merged_with_all = pd.merge(service_line, assessor_selected, on="address", how="left")

# Identify unmatched service line addresses (where assessor data is missing)
unmatched_service_lines = merged_with_all[merged_with_all["geocode_muni"].isna()]

# Save unmatched addresses to a CSV
unmatched_service_lines.to_csv("unmatched_service_lines.csv", index=False)

# Print summary
print(f"Total unmatched service line addresses: {len(unmatched_service_lines)}")

  
# Save matches to CSV files.
merged_matched.to_csv("matched_addresses.csv", index=False)

# Create dataframes for duplicate addresses
# Allows us to see which addresses have multiple rows due to conditions listed above
service_line_duplicates = service_line[service_line.duplicated(subset=["address"], keep=False)]
assessor_duplicates = assessor[assessor.duplicated(subset=["address"], keep=False)]

# Save duplicates to CSV
# Duplicates are saved 
service_line_duplicates.to_csv("service_line_duplicates.csv", index=False)
assessor_duplicates.to_csv("assessor_address_duplicates.csv", index=False)

# Print summary
print(f"Total matched addresses saved: {len(merged_matched)}")
print(f"Total duplicate matches based on address before merging: {duplicate_count}")
print(f"Total duplicates in service line: {len(service_line_duplicates)}")
print(f"Duplicates in assessor:  {len(assessor_duplicates)}")