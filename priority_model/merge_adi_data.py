"""
---------------------------------DEPRECATED-----------------------------------------
ADI score now calculated in col_score module to simplify steps

This Module uses the Neighborhood Atlas's block group ADI data to attatch scores to our chicago block group data
Uses state ADI scores 

Inputs:
    - Chicago Block Groups: 'chicago_block_groups.geojson' 
    - IL ADI Data: 'IL_2022_ADI_Census_Block_Group_v4_0_1' 

Outputs: 
    - Returns: Geodata frame (Chicago block groups with ADI scores)
    - Visualization: 'ADI_Score.png'
"""

import config
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

def load_and_merge_adi_scores(adi_path, cbg_path= None, cbg= None):
    """
    Gets ADI score for each block group from census data and merge that into the chicago block group dataframe
    Uses state rank to better capture chicago compared to other block groups in the state.

    Args:
        adi_path (str): File path to ADI data
        cbg_path (str): File path to chicago block group data
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups with ADI data
    """

    print("Merging ADI score into dataframe")

    # Read data
    adi = pd.read_csv(adi_path)
    if cbg is not None:
       print("Using provided GeoDataFrame") 
    elif cbg_path is not None:
        cbg = gpd.read_file(cbg_path)
    else:
        raise ValueError('Must provide either \'cbg\' (GeoDataFrame) or a valid \'cbg_path\' (string).')
        
    # Change column name to merge easier
    adi = adi.rename(columns={"FIPS": "GEOID"})
    # Read as string or it gets funky
    cbg["GEOID"] = cbg["GEOID"].astype(str)
    adi["GEOID"] = adi["GEOID"].astype(str)

    # For block groups without score set to 5 
    def clean_adi_rank(val):
        try:
            return int(val)
        except:
            return 5

    print("Cleaning data (filling empty scores)")
    adi["ADI_Score"] = adi["ADI_STATERNK"].apply(clean_adi_rank)

    print("Merging ADI score to dataframe")
    cbg = cbg.merge(
        adi[["GEOID", "ADI_Score"]],
        on="GEOID",
        how="left"
    )

    return cbg

def plot_adi_scores(cbg, output_path=config.MAPS_OUT + "ADI_Score.png"):
    """Plot and save adi score map"""
    fig, ax = plt.subplots(figsize=(10, 10))
    cbg.plot(
        ax=ax,
        column="ADI_Score",
        cmap="Blues",
        edgecolor="black",
        legend=True,
        missing_kwds={"color": "red", "label": "Missing data"}
    )
    ax.set_title("ADI Score")
    plt.axis("off")
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    #plt.show()

def main():
    print("Running merge_adi_data.py")

    merged = load_and_merge_adi_scores(
        config.ADI_DATA,
        config.GEOJSON_OUT + "chicago_block_groups_with_acs.geojson"
    )

    print("Saving file to " + config.GEOJSON_OUT)
    merged.to_file(config.GEOJSON_OUT + "chicago_block_groups_with_acs_adi.geojson", driver="GeoJSON")
    # merged.to_csv("../outputs/ChicagoBlockGroupsWithACS_ADI.csv")  # Optional CSV export
    
    plot_adi_scores(merged)

if __name__ == "__main__":
    main()
