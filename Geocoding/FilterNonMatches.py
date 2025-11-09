## Check addresses that have no match

import pandas as pd
import numpy as np
import os    

# Set current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load service line data
df = pd.read_csv("./ExpandedGeocodeBatches/Merged.csv")

no_match_df = df[df["Match_Type"].isna() | (df["Match_Type"].str.strip() == "")]

no_match_csv_path = "./ExpandedGeocodeBatches/No_Match_Addresses.csv"
no_match_df.to_csv(no_match_csv_path, index=False)

print(f"Saved {len(no_match_df)} unmatched addresses to {no_match_csv_path}")