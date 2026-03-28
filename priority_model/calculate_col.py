"""
This Module calculates a Cost of Living score for block groups in Chicago based off of Census ADI data and the number of children under 5
COL Score is a score of 1-10 determining the vulnerability of the population with 10 being a highly vulnerable population.

Inputs:
    - Chicago Block Groups (With ACS and ADI scores)

Outputs: 
    - Returns: Geodata Frame (Chicago block groups with COL score) 
    - Visualization: 'COL_Score.png'
"""

import config
import geopandas as gpd
import matplotlib.pyplot as plt

def calculate_col(cbg_path, cbg= None):
    """
    Calculates a COL score from the ACS and ADI scores
    COL = 0.5 * ACS_SCORE + 0.5 * ADI_SCORE

    Args:
        cbg_path (str): File path to chicago block group data
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups with ADI data
    """
    print("Calculating COL Score")
    if cbg is None:
        cbg = gpd.read_file(cbg_path)

    cbg["CoL"] = 0.5 * cbg["ADI_Score"] + 0.5 * cbg["ACS_Score"]

    return cbg

    

def plot_col_scores(cbg, output_path = None):
    """Plot and save col score map"""
    fig, ax = plt.subplots(figsize=(10, 10))
    cbg.plot(
        ax=ax,
        column="CoL",
        cmap="OrRd",
        edgecolor="black",
        legend=True,
        missing_kwds={"color": "Blues", "label": "Missing data"}
    )

    ax.set_title("CoL Score")
    plt.axis("off")
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    #plt.show()

def main():
    print("Running calculate_col.py")
    cbg = calculate_col(config.CHICAGO_BLOCK_GROUPS_ACS_ADI)

    print("Saving file to " + config.GEOJSON_OUT)
    cbg.to_file(config.GEOJSON_OUT + "chicago_block_groups_with_col.geojson", driver="GeoJSON")

    plot_col_scores(cbg, config.MAPS_OUT + "CoLScore.png")

if __name__ == "__main__":
    main()
