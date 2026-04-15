import config
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely import wkt
import matplotlib.patches as mpatches

def project_service_lines_hundred_ft(street_segments_path=None, street_segments=None, service_line_path=None, service_line=None):
    # Load data    
    if street_segments is not None:
       print("Using provided GeoDataFrame") 
    elif street_segments_path is not None:
        street_segments = gpd.read_file(street_segments_path)
    else:
        raise ValueError('Must provide either \'street_segments\' (GeoDataFrame) or a valid \'street_segments_path\' (string).')

    if service_line is not None:
       print("Using provided GeoDataFrame") 
    elif service_line_path is not None:
        service_line = pd.read_csv(service_line_path)
    else:
        raise ValueError('Must provide either \'service_line\' (GeoDataFrame) or a valid \'service_lines_path\' (string).')
    
    
    gdf_service = gpd.GeoDataFrame(
        service_line,
        geometry= service_line['geometry'].map(wkt.loads),
        crs= "EPSG:4326"
    )
    
    risky_labels = ["L", "GRR", "U"]
    
    def is_risky(material):
        return str(material).strip().upper() in risky_labels
    
    gdf_service["is_risky"] = gdf_service["Classification for Entire Service Line"].apply(is_risky)
    
    # Join risky service lines to 100 ft segments
    risky_lines = gdf_service[gdf_service["is_risky"] == True]
    
    risky_lines = risky_lines.to_crs(epsg=3435)
    street_segments = street_segments.to_crs(epsg=3435)
    
    joined = gpd.sjoin_nearest(
        risky_lines,
        street_segments[["geometry"]],
        how="left",
        distance_col="dist_to_segment"
    )
    
    # Count how many risky lines fall within each segment
    risky_counts = joined.groupby(joined.index_right).size().reset_index(name="risky_count")
    
    # Merge counts into the original segments
    street_segments["risky_count"] = 0
    street_segments.loc[risky_counts["index_right"], "risky_count"] = risky_counts["risky_count"].values
    
    #print(street_segments["risky_count"])
    
    street_segments["length_ft"] = street_segments.geometry.length
    #print(street_segments["length_ft"])
    
    # Normalize risk count
    street_segments["risk_per_ft"] = street_segments["risky_count"] / street_segments["length_ft"]
    
    # Convert to risk per 100 ft
    street_segments["risk_per_100ft"] = street_segments["risk_per_ft"] * 100
    
    def score_risk(count):
        if count == 0:
            return 0
        elif count < 1:
            return 1
        elif count <= 2.5:
            return 2
        elif count <= 5:
            return 3
        else:
            return 4
    
    street_segments["risk_score"] = street_segments["risk_per_100ft"].apply(score_risk)
    
    print(street_segments["risk_score"].value_counts().sort_index())
    
    street_segments = street_segments.to_crs(epsg=4326)
    
    street_segments.to_file(config.GEOJSON_OUT + "service_line_replacement_per_100ft_segments.geojson", driver="GeoJSON")
    
    
    # Define categorical color mapping
    color_map = {
        0: "lightgrey",
        1: "#ffffb2",  # yellow
        2: "#fecc5c",  # light orange
        3: "#fd8d3c",  # orange
        4: "#e31a1c",  # red
    }
    
    # Map each score to its color
    street_segments["color"] = street_segments["risk_score"].map(color_map)
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 12))
    street_segments.plot(
        ax=ax,
        color=street_segments["color"],
        linewidth=2
    )
    
    # Define legend labels
    legend_labels = {
        0: "0",
        1: "< 1 per 100ft",
        2: "1–2.5 per 100ft",
        3: "2.5–5 per 100ft",
        4: "> 5 per 100ft"
    }
    
    # Create custom legend handles
    legend_handles = [
        mpatches.Patch(color=color_map[k], label=legend_labels[k])
        for k in sorted(color_map.keys())
    ]
    
    # Add legend
    ax.legend(handles=legend_handles, title="Risky Service Line Count", loc="lower left")
    
    plt.title("Risky Service Lines per 100 ft Segment")
    plt.axis("off")
    plt.savefig(config.MAPS_OUT + "RiskyServiceLinesPer100FT", dpi= 300, bbox_inches= "tight")
    plt.tight_layout()
    #plt.show()
    
def main():
    print("Running ServiceLinesPerHundredFeet.py")
    project_service_lines_hundred_ft(street_segments_path= config.STREET_MODEL_HUNDRED_FOOT, service_line_path=config.SERVICE_LINES) 

if __name__ == "__main__":
    main()