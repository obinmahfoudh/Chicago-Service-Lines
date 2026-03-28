"""
This Module uses the ACS B01001 (Census) table to find the number of children under 5 and add the data to our chicago block group data 
Creates bins for number of children under 5 to calculate a score for each block group. 

Inputs:
    - Chicago Block Groups: 'chicago_block_groups.geojson'
    - IL ACS Data (Cook and Dupage Counties): 'CSDT5Y2022.B01001-Data.csv'

Outputs: 
    - Returns: Geodata frame (Chicago block groups with ACS scores)
    - Visualization: 'ACS_Score.png'
"""

import config
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

def load_and_merge_acs_data(acs_path, cbg_path, cbg= None):

    """
    Calculates an ACS score for each block group in Chicago based on the number of children under 5 within that block group 
    ACS score metrics taken from safe water engineering

    Args:
        acs_path (str): File path to ACS data
        cbg_path (str): File path to chicago block group data
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups with acs data
    """

    print("Merging ACS scores into dataframe")

    # Read data
    acs_data = pd.read_csv(acs_path)
    if cbg is None:
        cbg = gpd.read_file(cbg_path)

    print("Counting children under 5")
    # Male <5
    acs_data["B01001_003E"] = pd.to_numeric(acs_data["B01001_003E"], errors='coerce')  
    # Female <5
    acs_data["B01001_027E"] = pd.to_numeric(acs_data["B01001_027E"], errors='coerce')  
    acs_data["children_under_5"] = acs_data["B01001_003E"] + acs_data["B01001_027E"]

    print("Scoring block groups")
    def scoreACS(number):
        """Set ACS score for block group depending on number of children under 5 present"""
        if number == 0:
            return 1
        elif number <= 10:
            return 3
        elif number <= 50:
            return 5
        else:
            return 10

    # Apply score
    acs_data["ACS_Score"] = acs_data["children_under_5"].apply(scoreACS)

    # Rename block group column to match ACS data column name
    acs_data.rename(columns={"GEO_ID": "GEOIDFQ"}, inplace= True)
    print("Merging data to dataframe")
    # Merge
    cbg = cbg.merge(
        acs_data[["GEOIDFQ", "ACS_Score"]],
        on="GEOIDFQ",
        how="left"
    )

    print("/nACS Score distribution")
    print(f"Total block groups: {len(cbg)}")
    print(cbg["ACS_Score"].value_counts().sort_index())

    return cbg
    

def plot_acs_scores(cbg, output_path=None):
    """Plot and save acs score map"""
    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    cbg.plot(
        ax=ax,
        column="ACS_Score",
        cmap="Blues",
        edgecolor="black",
        legend=True,
        missing_kwds={"color": "red", "label": "Missing data"}
    )
    ax.set_title("ACS score (Chicago)")
    plt.axis("off")
    if output_path:
        plt.savefig(output_path)
    #plt.tight_layout()
    #plt.show()

def main():
    print("Running merge_acs_scores.py")

    merged = load_and_merge_acs_data(
        config.ACS_DATA, 
        config.CHICAGO_BLOCK_GROUPS
    )

    print("Saving file to " + config.GEOJSON_OUT)
    merged.to_file(config.GEOJSON_OUT + "chicago_block_groups_with_acs.geojson", driver="GeoJSON")
    # merged.to_csv("../outputs/ChicagoBlockGroupsWithACS_ADI.csv")  # Optional CSV export

    plot_acs_scores(merged, config.MAPS_OUT + "ACS_Score.png")

if __name__ == "__main__":
    main()
