import pandas as pd
import numpy as np
import os    

# Set current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Load service line data
service_line = pd.read_csv("../T096318_Responsive_Document.csv")
print(len(service_line))
service_line = service_line.drop_duplicates(subset=["Address"])
print(len(service_line))

# Handling Duplicates in Service Line Data
# ---------------------------------------

# Define priority order for materials
priority_order = {
    "LEAD": 4,
    "SUSPECTED LEAD": 3,
    "GALVANIZED NEEDS REPLACEMENT": 2,
    "NOT LEAD": 1
}

# Convert material descriptions to priority values
service_line["Material Priority"] = service_line["Private Service Line Material"].map(priority_order)

# Sort rows so that higher priority materials appear first
service_line.sort_values(by=["Address", "Material Priority"], ascending=[True, False], inplace=True)

# Dictionary to track addresses where "LEAD" and "NOT LEAD" both exist
conflicting_addresses = {}

# List to hold cleaned service line rows
cleaned_rows = []

# Process duplicates, ensuring we keep the correct rows
for address, group in service_line.groupby("Address"):
    materials = group["Private Service Line Material"].tolist()
    
    # Track addresses that have both "LEAD" and "NOT LEAD"
    if "LEAD" in materials and "NOT LEAD" in materials:
        conflicting_addresses[address] = len(group)
    
    # Remove "NOT LEAD" only if another material exists
    filtered_group = group[group["Private Service Line Material"] != "NOT LEAD"] if len(materials) > 1 else group
    
    cleaned_rows.append(filtered_group)

# Reconstruct cleaned dataframe
service_line_cleaned = pd.concat(cleaned_rows).drop(columns=["Material Priority"])

# Print count of conflicting addresses
print(f"Conflicting addresses count: {len(conflicting_addresses)}")

# Save conflicting addresses for review
pd.DataFrame.from_dict(conflicting_addresses, orient="index", columns=["Count"]).to_csv("./conflicting_addresses.csv")