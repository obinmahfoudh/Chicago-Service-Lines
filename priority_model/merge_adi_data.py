import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd

def load_and_merge_adi_data(adi_path, cbg_path):
    adi = pd.read_csv(adi_path)
    cbg = gpd.read_file(cbg_path)

    # Change column name to merge easier
    adi = adi.rename(columns={"FIPS": "GEOID"})
    # Read as string or it gets funky
    cbg["GEOID"] = cbg["GEOID"].astype(str)
    adi["GEOID"] = adi["GEOID"].astype(str)

    # For block groups without score just use 5
    def clean_adi_rank(val):
        try:
            return int(val)
        except:
            return 5

    adi["ADI_Score"] = adi["ADI_STATERNK"].apply(clean_adi_rank)

    merged = cbg.merge(
        adi[["GEOID", "ADI_Score"]],
        on="GEOID",
        how="left"
    )

    return merged

def plot_adi_scores(cbg, output_path=None):
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
    plt.show()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    merged = load_and_merge_adi_data(
        "../data/IL_2022_ADI_Census_Block_Group_v4_0_1.csv",
        "../outputs/geojsons/chicago_block_groups_with_acs.geojson"
    )

    merged.to_file("../outputs/geojsons/chicago_block_groups_with_acs_adi.geojson", driver="GeoJSON")
    # merged.to_csv("../outputs/ChicagoBlockGroupsWithACS_ADI.csv")  # Optional CSV export

    plot_adi_scores(merged, "../outputs/maps/ADI_Score.png")

if __name__ == "__main__":
    main()
