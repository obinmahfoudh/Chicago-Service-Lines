import config
import geopandas as gpd
import matplotlib.pyplot as plt
from . import visualization
import pandas as pd
from shapely import wkt

def calculate_lol_and_cost(df_service_path, cbg_path= None, cbg= None):
    """
    Calculates LoL score for each service line then finds the average for each block group
    Also calculates the number of risky service lines by: public line classification, private line classification, entire line classification 
    Then calculates minimum and maximum cost for partial and full service line replacement`

    Args:
        gdf_service_path (str): File path to Service Line data
        cbg_path (str): File path to chicago block group data
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups with LoL Scores
    """
    gdf_service = pd.read_csv(df_service_path)
    gdf_service = gpd.GeoDataFrame(
        gdf_service,
        geometry= gdf_service['geometry'].map(wkt.loads),
        crs= "EPSG:4326"
    )

    if cbg is not None:
       print("Using provided GeoDataFrame") 
    elif cbg_path is not None:
        cbg = gpd.read_file(cbg_path)
    else:
        raise ValueError('Must provide either \'cbg\' (GeoDataFrame) or a valid \'cbg_path\' (string).')

    
    def score_LoL(material):
        """Assign score to service line depending on material"""
        material = str(material).strip().upper()
        if "L" in material or "GRR" in material:
            return 10
        elif "U" in material:
            return 5
        elif "C" in material:
            return 0  # treating all copper as non-lead
        else:
            return 0  # for any other non-lead verified types
    
    # Apply scores to each service line
    print("Scoring service lines")
    gdf_service["LoL"] = gdf_service["Classification for Entire Service Line"].apply(score_LoL)
    gdf_service["PublicLoL"] = gdf_service["PWS-Owned Service Line Material"].apply(score_LoL)
    gdf_service["PrivateLoL"] = gdf_service["Customer Side Service Line Material"].apply(score_LoL)

    # Map service lines to block groups 
    cbg = cbg.to_crs("EPSG:4326")
    print("Mapping service lines to block groups")
    joined_service_lines = gpd.sjoin(gdf_service, cbg[["GEOID", "geometry"]], how="left", predicate="within")
    joined_service_lines = joined_service_lines.drop_duplicates(subset= 'Unique ID')
    
    # Group block groups and calculate the average LoL score of all service lines within them
    print("Averaging scores per block group")
    joined_block_groups = joined_service_lines.groupby("GEOID")["LoL"].mean().reset_index()

    # Calculate counts and costs of risky service lines replacement
    joined_block_groups = calculate_costs(joined_service_lines, joined_block_groups)

    print("Merging scores to block groups")
    cbg = cbg.merge(joined_block_groups, on="GEOID", how="left")
    cbg = cbg.fillna(0)
    return cbg
    
def calculate_costs(joined_service_line, joined_block_groups):
    """Calculates the cost for public service line, private service line and entire servvice line using a given min and max cost."""
    print("Calculating risky public and private sides")
    
    # Risky public side: PublicLoL in [10, 5]
    public_risky = joined_service_line[joined_service_line["PublicLoL"].isin([10, 5])]
    public_counts = public_risky.groupby("GEOID").size().reset_index(name="public_risky_count")

    # Risky private side: PrivateLoL in [10, 5]
    private_risky = joined_service_line[joined_service_line["PrivateLoL"].isin([10, 5])]
    private_counts = private_risky.groupby("GEOID").size().reset_index(name="private_risky_count")

    # Risky ENTIRE line
    entire_risky = joined_service_line[joined_service_line["LoL"].isin([10, 5])]
    entire_counts = entire_risky.groupby("GEOID").size().reset_index(name="entire_risky_count")

    # Merge counts
    risky_counts = public_counts.merge(private_counts, on="GEOID", how="outer").merge(entire_counts, on="GEOID", how="outer").fillna(0)

    # Calculate cost of replacement
    risky_counts["Min_Cost_Partial"] = (risky_counts["public_risky_count"] + risky_counts["private_risky_count"]) * config.MIN_COST
    risky_counts["Max_Cost_Partial"] = (risky_counts["public_risky_count"] + risky_counts["private_risky_count"]) * config.MAX_COST

    risky_counts["Min_Cost_Entire"] = risky_counts["entire_risky_count"] * config.MIN_COST
    risky_counts["Max_Cost_Entire"] = risky_counts["entire_risky_count"] * config.MAX_COST

    # Now merge with the LoL average
    joined_block_groups = joined_block_groups.merge(
        risky_counts,   
        on="GEOID",
        how="left"
    )
    joined_block_groups = joined_block_groups.fillna(0)

    return joined_block_groups

    #print(cbg["Min_Cost_Partial"])
    #print(cbg["Min_Cost_Entire"])

def main():
    print("Running calculate_lol.py") 
    cbg = calculate_lol_and_cost(
        config.SERVICE_LINES,
        config.GEOJSON_OUT + "chicago_block_groups_with_col.geojson"
    )

    cbg.to_file(config.GEOJSON_OUT + "chicago_block_groups_with_col_lol_costs.geojson", driver= "GeoJSON")
    visualization.plot_scores(cbg, column=["LoL"])

if __name__ == "__main__":
    main()