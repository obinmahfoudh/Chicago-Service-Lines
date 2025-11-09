## Expands addresses and creates batch files of addresses for Census geocoding API
## Addresses that are a range of numbers e.g: 5712 16 will be expanded to multiple rows such as 5712, 5713, 5714, etc.
## Saves batches of 10,000 rows including headers.

import pandas as pd
import numpy as np
import os    

# Set current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load service line data
# Load header from row 6 (index 6, meaning skip first 6 rows)
headers = pd.read_excel("../T099020_Responsive_2024_Inventory.xlsx", skiprows=6, nrows=1).columns

# Now load actual data starting from row 18
service_line = pd.read_excel("../T099020_Responsive_2024_Inventory.xlsx", skiprows=16, names=headers)

print(headers)

#print(service_line.head(5))  # Check first few rows
#print(f"Number of rows: {len(service_line)}")
print("Done reading")

#print(service_line["Anonymized Service Address (for FOIA)"])

# Drop exact duplicates. Ex: 671 75 N Michigan Ave appears twice with same information
# Some address duplicates contain differing service line information. One might say suspected lead while the other says Galvanized needs replacement

#Arrays containing the addresses that are expandable and not expandable for future reference
unexpandable = []
expandable= []

# Function to create ending range value when ending number is just last digits
# For example the address 6355 57 S WASHTENAW AVE. We will take the ending range value 57 and return the value 6357.
# This lets us iterate the range and expand addresses easier.
def ExpandAddresses(row):
    # Start by splitting off ', Chicago, IL ZIP' if it exists
    full_addr = row["Service Address"]
    base_address = full_addr.split(",")[0].strip()  # Get just "9533 S YALE AVE"

    address_parts = base_address.split()
    
    row = row.copy()

    # Extract ZIP code

    zip_code = full_addr.split(",")[-1].strip().split()[-1]
    row["ZIP"] = zip_code
   

    # Handle address ranges like "1200 00"
    if len(address_parts) >= 3 and address_parts[0].isdigit() and address_parts[1].isdigit():
        first_number = address_parts[0]
        remainder = ' '.join(address_parts[2:])
        row["Address"] = f"{first_number} {remainder}"
        expandable.append(full_addr)
    else:
        row["Address"] = base_address
        unexpandable.append(full_addr)

    return [row]

print("Cleaning")
# Create an empty list to hold all the expanded addresses with their corresponding data
expanded_addresses = []
# Loop over each row and expand addresses with ranges
for index, row in service_line.iterrows():
    expanded_addresses.extend(ExpandAddresses(row))
    #print(address, expanded_address_list)

print("Adding neccessary columns for census api")
# Create a new DataFrame for expanded addresses with their corresponding data
expanded_df = pd.DataFrame(expanded_addresses)

expanded_df.reset_index(drop=True, inplace=True)

# Add required columns
expanded_df["Unique ID"] = expanded_df.index + 1
expanded_df["City"] = "Chicago"
expanded_df["State"] = "IL"

# Keep only relevant columns in final output
expanded_df = expanded_df[["Unique ID", "Address", "City", "State", "ZIP"]]

print("Saving file")
# Save the expanded data to a CSV file
expanded_df.to_csv("./ExpandedFirstAddressBatches/expanded_first_service_line_info.csv", index=False)

print("Creating batches")
#Create batches of size 10,000 for census geocoder
batch_size = 9999
for i in range(0, len(expanded_df), batch_size):
    batch = expanded_df.iloc[i:i+batch_size]
    batch.to_csv(f"./ExpandedFirstAddressBatches/geocode_address_batch_{i//batch_size + 1}.csv", index=False)
