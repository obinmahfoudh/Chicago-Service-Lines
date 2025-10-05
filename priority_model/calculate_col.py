import geopandas as gpd
import matplotlib.pyplot as plt
import os

def calculate_col(data_path):
    # Set working directory
    print("Reading file")
    cbg = gpd.read_file(data_path)
    print("Calculating scores")
    cbg["CoL"] = 0.5 * cbg["ADI_Score"] + 0.5 * cbg["ACS_Score"]

    return cbg

    

def plot_col_scores(cbg, output_path = None):
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
    plt.savefig("CoL Score")
    plt.show()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    path = "../outputs/geojsons/chicago_block_groups_with_acs_adi.geojson"

    cbg = calculate_col(path)
    cbg.to_file("../outputs/geojsons/chicago_block_groups_with_col.geojson", driver="GeoJSON")

    plot_col_scores(cbg, "../outputs/maps/CoLScore")

    

if __name__ == "__main__":
    main()