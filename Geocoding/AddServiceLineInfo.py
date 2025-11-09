## Merges service line data with matches assessor data
## Checks for matches in address and mailing_address column
## Saves a csv with matched data
## Saves a csvs for duplicate rows from address, mailing_address and service line address

import pandas as pd
import os    


os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load CSV files
df1 = pd.read_csv("./ExpandedFirstGeocodeBatches/Merged.csv")
# Load header from row 6 (index 6, meaning skip first 6 rows)
headers = pd.read_excel("../T099020_Responsive_2024_Inventory.xlsx", skiprows=6, nrows=1).columns

# Now load actual data starting from row 18
df2 = pd.read_excel("../T099020_Responsive_2024_Inventory.xlsx", skiprows=16, names=headers)

# Add required columns
df2["Unique ID"] = df2.index + 1
# Merge on 'Unique ID' and 'Address' columns (modify column names if needed)
merged_df = df1.merge(df2, on=["Unique ID"], how="left") 

# Save the merged file
merged_df.to_csv("./ExpandedFirstGeocodeBatches/merged_file.csv", index=False)

print("Merge complete. File saved as 'merged_file.csv'")

