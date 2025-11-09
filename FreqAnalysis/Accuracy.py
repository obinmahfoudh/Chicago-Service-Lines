import pandas as pd
import os    


os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load Data
matched_addresses = pd.read_csv("./matched_addresses.csv")  
service_line_connections = pd.read_csv("./service_line_with_connections.csv")  

# Add an explicit index column to matched_addresses
matched_addresses.reset_index(inplace=True)
matched_addresses.rename(columns={"index": "Matched_Index"}, inplace=True)

# Convert 'Connected_Assessor_Addresses' from string to list (if stored as a string)
service_line_connections["Connected_Assessor_Addresses"] = service_line_connections["Connected_Assessor_Addresses"].apply(
    lambda x: eval(x) if isinstance(x, str) else x  # Convert string to list safely
)

# Filter matched addresses to exclude "no match" entries
valid_matches = matched_addresses[matched_addresses["match_type"] != "no match"].copy()

# Merge matched addresses with service line connections based on 'Unique ID'
merged_data = valid_matches.merge(service_line_connections, left_on="Unique ID", right_on="Unique ID", how="left")

# Check if the matched address exists in the connected assessor addresses
merged_data["Match_Confirmed"] = merged_data.apply(
    lambda row: row["matched_address"] in row["Connected_Assessor_Addresses"] if isinstance(row["Connected_Assessor_Addresses"], list) else False, 
    axis=1
)

# Count total matches and confirmed matches
total_matches = len(merged_data)
confirmed_matches = merged_data["Match_Confirmed"].sum()
accuracy = (confirmed_matches / total_matches) * 100 if total_matches > 0 else 0

# Print results
print(f"Total Matches Checked: {total_matches}")
print(f"Confirmed Matches: {confirmed_matches}")
print(f"Accuracy: {accuracy:.2f}%")

# Save results
merged_data.to_csv("./MatchedAccuracyCheck.csv", index=False)

print("Accuracy check complete! Results saved as MatchedAccuracyCheck.csv.")
