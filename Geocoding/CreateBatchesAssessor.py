## Expands addresses and creates batch files of addresses for Census geocoding API
## Addresses that are a range of numbers e.g: 5712 16 will be expanded to multiple rows such as 5712, 5713, 5714, etc.
## Saves batches of 10,000 rows including headers.

import pandas as pd
import numpy as np
import os    

# Set current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load service line data
df = pd.read_csv("../Assessor__Archived_05-11-2022__-_Property_Locations_20250225.csv")

# Add column name for address. Add other data that the census geocoder requires
df = df[['property_address']].copy()
df["Unique ID"] = df.index+1
df['City'] = 'Chicago'
df['State'] = 'IL'
df['ZIP'] = np.nan

#Reorganize columns so unique id is first
column_order = ["Unique ID"] + [col for col in df.columns if col != "Unique ID"]
df = df[column_order]

df.to_csv("./AssessorGeocodeBatches/AssessorGeocodeAddresses.csv")

batch_size = 9999
for i in range(0, len(df), batch_size):
    batch = df.iloc[i:i+batch_size]
    batch.to_csv(f"./AssessorGeocodeBatches/assessor_geocode_batch{i//batch_size + 1}.csv", index=False)