import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load CSV files
folder_path = "./ExpandedFirstGeocodeBatches"
output_file = os.path.join(folder_path, "Merged.csv")

# Get all batch result CSV files
csv_files = [f for f in os.listdir(folder_path) if f.startswith("geocode_address_batch") and f.endswith("_geocoderesult.csv")]

dfs = []

for file in csv_files:
    file_path = os.path.join(folder_path, file)
    
    try:
        # Read CSV without assuming a header and enforce column count
        df = pd.read_csv(file_path, header=None, delimiter=",", dtype=str, keep_default_na=False)
        
        # Ensure all dataframes have the same number of columns
        if len(df.columns) != 8:
            print(f"Warning: {file} has {len(df.columns)} columns instead of 8. Fixing...")
            df = df.iloc[:, :8]  # Trim extra columns or pad missing ones
        
        dfs.append(df)
    
    except Exception as e:
        print(f"Error reading {file}: {e}")

# Merge all dataframes correctly
if dfs:
    merged = pd.concat(dfs, ignore_index=True)
    merged.to_csv(output_file, index=False, header=False)
    print(f"Merged file saved to {output_file}")
else:
    print("No valid CSV files found for merging.")
