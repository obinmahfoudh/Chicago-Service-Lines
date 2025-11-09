import pandas as pd
import numpy as np
import os
from scipy.spatial import cKDTree

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Load Data
assessor = pd.read_csv("./AssessorGeocode.csv") 
service_line = pd.read_csv("./ServiceLineGeocodeProperExpansion.csv")  

i = 1

# Function to extract Lat & Long from Geodata column
def extract_lat_long(geodata):
    global i
    try:
        lon, lat = map(float, geodata.split(","))
        print(f"Good Row {i}")
        i+=1
        return lat, lon  
    except:
        print(f"Error Row {i}")
        i+=1
        # Handle missing or malformed data
        return np.nan, np.nan  


# Drop rows where 'Geodata' is empty
assessor.dropna(subset=['Geodata'], inplace=True)
service_line.dropna(subset=['Geodata'], inplace=True)

# Apply extraction to both datasets
assessor[['Lat', 'Long']] = assessor['Geodata'].apply(lambda x: pd.Series(extract_lat_long(str(x))))
i= 1
service_line[['Lat', 'Long']] = service_line['Geodata'].apply(lambda x: pd.Series(extract_lat_long(str(x)))) 


# Convert coordinates to NumPy arrays for vectorized distance calculation
assessor_coords = assessor[['Lat', 'Long']].to_numpy()
service_coords = service_line[['Lat', 'Long']].to_numpy()


# Compute distance matrix using Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c  # Returns distance in km

# Convert service line coordinates into a KDTree for fast lookup
service_tree = cKDTree(service_coords)

# Find nearest neighbor for each assessor
assessor_coords = assessor[['Lat', 'Long']].to_numpy()
distances, indices = service_tree.query(assessor_coords)

# Add matched service line index to assessor dataset
assessor["Closest_Service_Index"] = indices

# Create a dictionary to store connected assessor addresses per service line
service_line_map = {i: [] for i in range(len(service_line))}

# Populate the dictionary
for assessor_index, service_index in enumerate(indices):
    assessor_address = assessor.iloc[assessor_index]['Address']
    service_line_map[service_index].append(assessor_address)

# Convert dictionary to lists for DataFrame columns
service_line["Connected_Assessor_Addresses"] = service_line.index.map(lambda i: service_line_map[i])
service_line["Num_Connected_Addresses"] = service_line["Connected_Assessor_Addresses"].apply(len)

# Save the updated service line data
service_line.to_csv("service_line_with_connections.csv", index=False)

print("Processing complete! File saved as service_line_with_connections.csv")
