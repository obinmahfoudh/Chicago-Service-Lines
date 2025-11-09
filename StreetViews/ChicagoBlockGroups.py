import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.wkt import dumps
import os


# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Read files
print("Loading chicago boundaries")
chicagoBoundaries = pd.read_csv("./Geometries/City_Boundary_20250424.csv")
print("Loading Il block groups")
gdf_bg = gpd.read_file("./Geometries/IL_BlockGroups/tl_2023_17_bg.shp")

print("Converting chicago boundaries to pandas geometry")
#Convert multipolygon to wkt
chicagoBoundaries["geometry"] = chicagoBoundaries["the_geom"].apply(wkt.loads)
gdf_chicago = gpd.GeoDataFrame(chicagoBoundaries, geometry="geometry", crs="EPSG:4326")

print("Matching coordinate systems")
gdf_bg = gdf_bg.to_crs(gdf_chicago.crs)

print("Filtering IL block groups to those in Chicago")
chicago_block_groups = gpd.sjoin(gdf_bg, gdf_chicago, how="inner", predicate="intersects")

print("Saving block group data as geoJson")
chicago_block_groups.to_file("./Geometries/chicago_block_groups.geojson", driver="GeoJSON")

print("Converting geometry to wkt and saving as csv")
# Convert geometry column to WKT strings
chicago_block_groups["geometry_wkt"] = chicago_block_groups.geometry.apply(dumps)

# Save to CSV with WKT included
chicago_block_groups.drop(columns="geometry").to_csv("./chicago_block_groups_with_wkt.csv", index=False)

print("Filtered block groups saved to 'chicago_block_groups.geojson'")
