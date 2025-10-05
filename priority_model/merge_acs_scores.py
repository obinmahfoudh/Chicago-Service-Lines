"""
This script uses the ACS B01001 table to find the number of children under 5 and add the data to our chicago block group data 
Creates bins for number of children under 5 to calculate a score for each block group. 
Refer to Read.me for methodology
Outputs:  ChicagoBlockGroupsWithACS.geojson 
"""
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

def load_and_merge_acs_data(acs_path, cbg_path):
    # Read data
    print("Reading data")
    acs_data = pd.read_csv(acs_path)
    cbg = gpd.read_file(cbg_path)

    

    print("Extracting data")
    acs_data["GEOID"] = acs_data["GEO_ID"].str.extract(r'US(\d{12})')[0]

    print("Merging dataframes")
    # Merge
    cbg = cbg.merge(
        acs_data[["GEOID", "B01001_003E", "B01001_027E"]],
        on="GEOID",
        how="left"
    )

    print("Counting children under 5")
    # Male <5
    cbg["B01001_003E"] = pd.to_numeric(acs_data["B01001_003E"], errors='coerce')  
    # Female <5
    cbg["B01001_027E"] = pd.to_numeric(acs_data["B01001_027E"], errors='coerce')  
    cbg["children_under_5"] = cbg["B01001_003E"] + cbg["B01001_027E"]

    print("Scoring block groups")
    # Define scoring function
    def scoreACS(number):
        if number == 0:
            return 1
        elif number <= 10:
            return 3
        elif number <= 50:
            return 5
        else:
            return 10

    # Apply score
    cbg["ACS_Score"] = cbg["children_under_5"].apply(scoreACS)

    print("ACS Score distribution:")
    print(f"Total block groups: {len(cbg)}")
    print(cbg["ACS_Score"].value_counts().sort_index())


    return cbg
    
    # Prints for debugging
    '''
    # Print block groups with missing ACS score
    missing_acs = cbg[cbg["ACS_Score"].isna()]
    print("Block groups with missing ACS data:")
    print(missing_acs[["GEOID"]])
    '''

def plot_acs_scores(cbg, output_path=None):
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
    plt.tight_layout()
    plt.show()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Running merge_acs_scores.py")

    merged = load_and_merge_acs_data(
        "../data/ACSDT5Y2022.B01001-Data.csv",
        "../outputs/geojsons/chicago_block_groups.geojson"
    )

    print("Saving file")
    merged.to_file("../outputs/geojsons/chicago_block_groups_with_acs.geojson", driver="GeoJSON")
    # merged.to_csv("../outputs/ChicagoBlockGroupsWithACS_ADI.csv")  # Optional CSV export

    plot_acs_scores(merged, "../outputs/maps/ACS_Score.png")

if __name__ == "__main__":
    main()
