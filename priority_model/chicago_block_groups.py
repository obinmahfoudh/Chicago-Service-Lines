"""
This Module uses Chicago's geometry (From Chicago data portal) as well as IL block group geometries (Census data)
to get the block groups for the City of Chicago.
Block groups are overlayed on the city of Chicago and only those intersecting are kept

Inputs:
    - Chicago Boundaries: 'CityBoundaries.csv' (from Chicago Data Portal)
    - IL Block Groups: 'tl_2023_17_bg.shp' (from US Census)

Outputs:
    - GeoJSON: chicago_block_groups.geojson
    - Visualization: chicago_block_groups.png
    - (Optional) CSV: 'chicago_block_groups_with_wkt.csv' (Includes WKT geometry) 
"""

import config
import pandas as pd
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
from shapely.wkt import dumps

def filter_chicago_block_groups(chicago_bounds_path, block_group_path, save_wkt= False):
    """
    Overlays IL block groups over Chicago using intersects predicate to filter the block groups to those 
    within Chicago

    Removes large shape which appears to be lake Michigan

    Args:
        chicago_bounds_path (str): File path to Chicago geometry shapefile
        block_group_path (str): File path to IL block group shapefile
        save_wkt (boolean): If true saves chicago block group data as a csv with a wkt column for the geometry
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups
    """

    #Read files
    print("Loading chicago boundaries")
    df_chicago_boundaries = pd.read_csv(chicago_bounds_path)
    print("Loading Il block groups")
    gdf_bg = gpd.read_file(block_group_path)

    print("Converting chicago boundaries to pandas geometry")
    #Convert multipolygon to wkt
    df_chicago_boundaries["the_geom"] = df_chicago_boundaries["the_geom"].apply(wkt.loads)
    gdf_chicago = gpd.GeoDataFrame(df_chicago_boundaries, geometry="the_geom", crs="EPSG:4326")

    print("Matching coordinate systems")
    gdf_bg = gdf_bg.to_crs(gdf_chicago.crs)

    # Used intersects in order to get all the block groups as some were a little outside the boundaries
    # Can change predicate to within to be more strict.
    print("Filtering IL block groups to those in Chicago")
    chicago_block_groups = gpd.sjoin(gdf_bg, gdf_chicago[['the_geom']], how="inner", predicate="intersects")
    chicago_block_groups = chicago_block_groups.drop(columns='index_right')

    # There is a large shape that appears when using intersects. I believe it is Lake Michigan
    # This removes the geometry with the largest area
    chicago_block_groups_proj = chicago_block_groups.to_crs("EPSG:26971")
    chicago_block_groups_proj["area_m2"] = chicago_block_groups_proj.geometry.area
    largest_idx = chicago_block_groups_proj["area_m2"].idxmax()
    chicago_block_groups_proj = chicago_block_groups_proj.drop(index=largest_idx).reset_index(drop=True)

    cbg = chicago_block_groups_proj.to_crs("EPSG:4326")

    print("Saving block group data as geoJson")
    cbg.to_file(config.GEOJSON_OUT + "chicago_block_groups.geojson", driver="GeoJSON")
    
    # Optional save geometries as csv in WKT format
    if save_wkt:
        print("Converting geometry to wkt and saving as csv")
        # Convert geometry column to WKT strings
        chicago_block_groups["geometry_wkt"] = chicago_block_groups.geometry.apply(dumps)
        # Save to CSV with WKT included
        chicago_block_groups.drop(columns="geometry").to_csv("./chicago_block_groups_with_wkt.csv", index=False)

    print("Block groups saved to 'chicago_block_groups.geojson'")
    return cbg

    
def plot_block_groups(cbg, output_path = config.MAPS_OUT + "Chicago_Block_Groups.png"):
    """Plots Chicago block groups and saves as a png"""
    # Plot
    cbg.plot(figsize=(10, 10), edgecolor='black')
    plt.title("Chicago Block Groups")
    plt.axis('off')
    if output_path:
        plt.savefig(output_path)
    plt.show()

def main():
    print("Running get_chicago_block_groups.py")
    cbg = filter_chicago_block_groups(
        config.CITY_BOUNDS,
        config.IL_BLOCK_GROUPS
    )

    plot_block_groups(cbg)

if __name__ == "__main__":
    main()
