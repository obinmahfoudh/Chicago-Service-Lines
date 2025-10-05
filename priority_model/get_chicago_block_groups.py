## This script uses the chicago geometry (Chicago data portal) as well as IL block group geometries (Census data)
## in order to get the block groups for the City of Chicago.
## Outputs a geojson with chicago block groups

import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.wkt import dumps
import os
import matplotlib.pyplot as plt


def filter_chicago_block_groups(chicago_bounds_path, block_group_path):
    # Set working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Running get_chicago_block_groups.py")

    #Read files
    print("Loading chicago boundaries")
    chicagoBoundaries = pd.read_csv(chicago_bounds_path)
    print("Loading Il block groups")
    gdf_bg = gpd.read_file(block_group_path)

    print("Converting chicago boundaries to pandas geometry")

    #Convert multipolygon to wkt
    chicagoBoundaries["geometry"] = chicagoBoundaries["the_geom"].apply(wkt.loads)
    gdf_chicago = gpd.GeoDataFrame(chicagoBoundaries, geometry="geometry", crs="EPSG:4326")

    print("Matching coordinate systems")
    gdf_bg = gdf_bg.to_crs(gdf_chicago.crs)

    # Used intersects in order to match some of the streets in the street centerline data as they were a little outside of chicago
    # Can change predicate to within to be more strict.
    print("Filtering IL block groups to those in Chicago")
    chicago_block_groups = gpd.sjoin(gdf_bg, gdf_chicago, how="inner", predicate="intersects")

    # There is a large shape that appears when using intersects. I believe it is Lake Michigan
    # This removes the geometry with the largest area
    chicago_block_groups_proj = chicago_block_groups.to_crs("EPSG:26971")
    chicago_block_groups_proj["area_m2"] = chicago_block_groups_proj.geometry.area
    largest_idx = chicago_block_groups_proj["area_m2"].idxmax()
    chicago_block_groups_proj = chicago_block_groups_proj.drop(index=largest_idx).reset_index(drop=True)

    cbg = chicago_block_groups_proj.to_crs("EPSG:4326")

    print("Saving block group data as geoJson")
    cbg.to_file("../outputs//geojsons/chicago_block_groups.geojson", driver="GeoJSON")

    # Can uncomment the below section to save geometries as csv
    #print("Converting geometry to wkt and saving as csv")
    # Convert geometry column to WKT strings
    #chicago_block_groups["geometry_wkt"] = chicago_block_groups.geometry.apply(dumps)
    #Save to CSV with WKT included
    #chicago_block_groups.drop(columns="geometry").to_csv("./chicago_block_groups_with_wkt.csv", index=False)

    print("Filtered block groups saved to 'chicago_block_groups.geojson'")
    return cbg

    
def plot_block_groups(cbg, output_path = None):
    # Plot
    cbg.plot(figsize=(10, 10), edgecolor='black')
    plt.title("Chicago Block Groups")
    plt.axis('off')
    if output_path:
        plt.savefig(output_path)
    plt.show()

def main():
    cbg = filter_chicago_block_groups(
        "../data/City_Boundary_20250424.csv",
        "../data/IL_BlockGroups/tl_2023_17_bg.shp"
    )

    plot_block_groups(cbg, "../outputs/maps/Chicago_Block_Groups.png")

if __name__ == "__main__":
    main()
