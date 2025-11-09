import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
from shapely.geometry import LineString, MultiLineString
from shapely.ops import substring
from shapely.geometry import Point
import matplotlib.patches as mpatches


# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

street_segments =  gpd.read_file("./Geometries/streets_100ft_segments.geojson")

service_line = pd.read_csv("../service_line_geocoded_fixed_final.csv")

print("Converting service line data to geometric points")
def geodata_to_point(geodata):
    try:
        lon, lat = map(float, geodata.split(','))
        return Point(lon, lat)
    except:
        return None
    
service_line["geometry"] = service_line["long_lat"].apply(geodata_to_point)
gdf_service = gpd.GeoDataFrame(service_line, geometry="geometry", crs="EPSG:4326")

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


street_segments.to_file("./Geometries/service_line_replacement_per_100ft_segments.geojson", driver="GeoJSON")

import matplotlib.patches as mpatches

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
plt.savefig("RiskyServiceLinesPer100FT", dpi= 300, bbox_inches= "tight")
plt.tight_layout()
plt.show()

