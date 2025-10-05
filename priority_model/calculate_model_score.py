import geopandas as gpd
import matplotlib.pyplot as plt
import os

def calculate_model_score(cbg_path):
    
    cbg = gpd.read_file(cbg_path)

    print("Calculating model scores")
    cbg["Model_Score"] = cbg["CoL"] * cbg["avg_LoL"]

    return cbg

def plot_model_score(cbg, output_path= None):
    fig, ax = plt.subplots(figsize=(10, 10))
    cbg.plot(
        ax=ax,
        column="Model_Score",
        cmap="OrRd",
        edgecolor="black",
        legend=True,
        missing_kwds={"color": "Blues", "label": "Missing data"}
    )

    ax.set_title("Model Priority Score")
    plt.axis("off")
    plt.tight_layout()
    if output_path:
        plt.savefig(output_path)
    plt.show()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    cbg = calculate_model_score(
        "../outputs/geojsons/chicago_block_groups_with_col_lol_costs.geojson"
    )

    print("Saving files")
    #cbg.to_csv("model_scores.csv")
    cbg.to_file("../outputs/geojsons/model_scores.geojson", driver="GeoJSON")
    plot_model_score(cbg, "../outputs/maps/ModelScore")

if __name__ == "__main__":
    main()