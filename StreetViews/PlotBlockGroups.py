import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
from shapely import wkt

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

chicagoBoundaries = pd.read_csv("./Geometries/City_Boundary_20250424.csv")

#Convert multipolygon to wkt
chicagoBoundaries["geometry"] = chicagoBoundaries["the_geom"].apply(wkt.loads)
gdf_chicago = gpd.GeoDataFrame(chicagoBoundaries, geometry="geometry", crs="EPSG:4326")

# Plot only the city boundary
gdf_chicago.plot(figsize=(10, 10), edgecolor='black', facecolor='lightblue')
plt.title("Chicago boundaries")
plt.show()

cbg = gpd.read_file("./Geometries/chicago_block_groups.geojson")

# This is the geoid of largest geometry
#cbg[cbg["GEOID"] == "170318360003"].plot()
# Project to distance crs to calculate area
chicago_block_groups_proj = cbg.to_crs("EPSG:26971")

# There is big chunk overlapping chicago area in map, I believe its supposed to be lake Michigan
# Removing largest geometry from data seems to remove it fine
chicago_block_groups_proj["area_m2"] = chicago_block_groups_proj.geometry.area
largest_idx = chicago_block_groups_proj["area_m2"].idxmax()
chicago_block_groups_proj = chicago_block_groups_proj.drop(index=largest_idx).reset_index(drop=True)

# print(chicago_block_groups_proj.loc[largest_idx])

cbg = chicago_block_groups_proj.to_crs("EPSG:4326")

cbg.to_file("./Geometries/chicago_block_groups.geojson", driver="GeoJSON")

# Plot
cbg.plot(figsize=(10, 10), edgecolor='black')
plt.title("Chicago Block Groups")
plt.axis('off')
plt.show()
