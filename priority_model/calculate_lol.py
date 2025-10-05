import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
from shapely.geometry import Point



def calculate_lol_and_cost(service_line_path, cbg_path):
    service_line = pd.read_csv(service_line_path)
    cbg = gpd.read_file(cbg_path)

    
    def score_LoL(material):
        material = str(material).strip().upper()
        if "L" in material or "GRR" in material:
            return 10
        elif "U" in material:
            return 5
        elif "C" in material:
            return 0  # treating all copper as non-lead
        else:
            return 0  # for any other non-lead verified types

    print("Scoring service lines")
    service_line["LoL"] = service_line["Classification for Entire Service Line"].apply(score_LoL)
    service_line["PublicLoL"] = service_line["PWS-Owned Service Line Material"].apply(score_LoL)
    service_line["PrivateLoL"] = service_line["Customer Side Service Line Material"].apply(score_LoL)


    print("Converting service line data to geometric points")
    def geodata_to_point(geodata):
        try:
            lon, lat = map(float, geodata.split(','))
            return Point(lon, lat)
        except:
            return None
        
    service_line["geometry"] = service_line["long_lat"].apply(geodata_to_point)
    gdf_service = gpd.GeoDataFrame(service_line, geometry="geometry", crs="EPSG:4326")
    cbg = cbg.to_crs("EPSG:4326")

    print("Mapping service lines to block groups")
    joined = gpd.sjoin(gdf_service, cbg[["GEOID", "geometry"]], how="left", predicate="within")

    print("Calculating risky public and private sides")
    
    # Risky public side: PublicLoL in [10, 5]
    public_risky = joined[joined["PublicLoL"].isin([10, 5])]
    public_counts = public_risky.groupby("GEOID").size().reset_index(name="public_risky_count")

    # Risky private side: PrivateLoL in [10, 5]
    private_risky = joined[joined["PrivateLoL"].isin([10, 5])]
    private_counts = private_risky.groupby("GEOID").size().reset_index(name="private_risky_count")

    # Risky ENTIRE line
    entire_risky = joined[joined["LoL"].isin([10, 5])]
    entire_counts = entire_risky.groupby("GEOID").size().reset_index(name="entire_risky_count")

    # Merge counts
    risky_counts = public_counts.merge(private_counts, on="GEOID", how="outer").merge(entire_counts, on="GEOID", how="outer").fillna(0)

    # Calculate cost of replacement
    risky_counts["Min_Cost_Partial"] = (risky_counts["public_risky_count"] + risky_counts["private_risky_count"]) * 8000
    risky_counts["Max_Cost_Partial"] = (risky_counts["public_risky_count"] + risky_counts["private_risky_count"]) * 16000

    risky_counts["Min_Cost_Entire"] = risky_counts["entire_risky_count"] * 16000
    risky_counts["Max_Cost_Entire"] = risky_counts["entire_risky_count"] * 32000

    print("Averaging scores per block group")
    lol_by_blockgroup = joined.groupby("GEOID")["LoL"].mean().reset_index()
    lol_by_blockgroup = lol_by_blockgroup.rename(columns={"LoL": "avg_LoL"})
    #print(cbg["Min_Cost_Partial"])
    #print(cbg["Min_Cost_Entire"])

    # Now merge with the LoL average
    lol_by_blockgroup = lol_by_blockgroup.merge(
        risky_counts,   
        on="GEOID",
        how="left"
    )

    lol_by_blockgroup = lol_by_blockgroup.fillna(0)

    print("Merging scores to block groups")
    cbg = cbg.merge(lol_by_blockgroup, on="GEOID", how="left")
    cbg = cbg.fillna(0)

    # Debugging prints
    #print("Original number of service lines:", len(service_line))
    #print("After spatial join:", len(joined))


    return cbg
    

def plot_lol(cbg, output_path = None):
    # Plot
    fig, ax = plt.subplots(figsize=(12, 12))
    cbg.plot(
        ax=ax,
        column="avg_LoL",
        cmap="Blues",
        edgecolor="black",
        linewidth=0.5,
        legend=True,
        missing_kwds={"color": "lightgrey", "label": "Missing data"},
        legend_kwds={
            "label": "Average Likelihood of Lead (LoL)",
            "orientation": "vertical",
            "shrink": 0.6
        }
    )

    # Center the map
    minx, miny, maxx, maxy = cbg.total_bounds
    buffer = 0.01
    ax.set_xlim(minx - buffer, maxx + buffer)
    ax.set_ylim(miny - buffer, maxy + buffer)

    ax.set_title("Average Likelihood of Lead (LoL) by Block Group", fontsize=14)
    plt.axis("off")
    if output_path:
        plt.savefig(output_path)
    plt.tight_layout()
    plt.show()

def main():
    # Set working directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    merged = calculate_lol_and_cost(
        "../data/service_line_geocoded_fixed_final.csv",
        "../outputs/geojsons/chicago_block_groups_with_col.geojson"
    )

    merged.to_file("../outputs/geojsons/chicago_block_groups_with_col_lol_costs.geojson", driver= "GeoJSON")
    plot_lol(merged, "../outputs/maps/AverageLoLScore")

if __name__ == "__main__":
    main()