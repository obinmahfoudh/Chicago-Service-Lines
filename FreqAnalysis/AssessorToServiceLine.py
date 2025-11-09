import pandas as pd
import numpy as np
import os
from scipy.spatial import cKDTree
from math import radians, cos, sin, sqrt, atan2

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Load Data
assessor = pd.read_csv("./AssessorLatLong.csv") 
service_line = pd.read_csv("./ServiceLineLatLong.csv")  
'''
i = 1

# Function to extract Lat & Long from Geodata column
def extract_lat_long(geodata):
    global i
    try:
        lon, lat = map(float, geodata.split(","))
        print(f"Good Row {i}")
        i+=1
        return lat, lon  # Ensure correct order: Latitude first, Longitude second
    except:
        print(f"Error Row {i}")
        i+=1
        return np.nan, np.nan  # Handle missing or malformed data


# Drop rows where 'Geodata' is empty
assessor.dropna(subset=['Geodata'], inplace=True)
service_line.dropna(subset=['Geodata'], inplace=True)

# Apply extraction to both datasets
assessor[['Lat', 'Long']] = assessor['Geodata'].apply(lambda x: pd.Series(extract_lat_long(str(x))))
i= 1
service_line[['Lat', 'Long']] = service_line['Geodata'].apply(lambda x: pd.Series(extract_lat_long(str(x)))) 



assessor.to_csv("./AssessorLatLong.csv")
service_line.to_csv("./ServiceLineLatLong.csv")
'''

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
distances, indices = service_tree.query(assessor_coords, k=2)

# Store matches and count corrections
corrected_count = 0
matched_service_lines = []

for i, (idx_nearest, idx_second) in enumerate(indices):
    lat1, lon1 = assessor_coords[i]
    
    # Get nearest service line from KDTree
    lat_nearest, lon_nearest = service_coords[idx_nearest]
    
    # Compute Haversine distance to nearest
    haversine_nearest = haversine(lat1, lon1, lat_nearest, lon_nearest)
    
    # Compute Haversine distance to second nearest
    lat_second, lon_second = service_coords[idx_second]
    haversine_second = haversine(lat1, lon1, lat_second, lon_second)
    
    # Decide if we need to switch
    if haversine_second < haversine_nearest:
        best_idx = idx_second
        corrected_count += 1
    else:
        best_idx = idx_nearest

    # Save full service line details
    matched_service_lines.append(service_line.iloc[best_idx].to_dict())

# Add matched service line indices to assessor data
assessor["matched_service_line_idx"] = matched_service_lines

# Add matched service line indices to assessor data
assessor["matched_service_line_idx"] = matched_service_lines

# Save results
assessor.to_csv("assessor_with_service_line_matches.csv", index=False)

# Print report
print(f"Total addresses: {len(assessor)}")
print(f"Total corrected by Haversine: {corrected_count}")
print(f"Percentage corrected: {corrected_count / len(assessor) * 100:.2f}%")
