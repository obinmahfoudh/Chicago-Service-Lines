import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
from shapely import wkt
from shapely.geometry import LineString, MultiLineString
from shapely.ops import substring
from shapely.geometry import Point


# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


model =  gpd.read_file("./Geometries/street_model_scores.geojson")


gdf_streets_proj = model.to_crs(epsg=3435)


def explode_and_split(geom):
    if isinstance(geom, MultiLineString):
        lines = geom.geoms
    elif isinstance(geom, LineString):
        lines = [geom]
    else:
        return []

    segments = []
    for line in lines:
        if line.length < 1:
            continue
        start = 0.0
        while start < line.length:
            end = min(start + 100, line.length)
            seg = substring(line, start, end)
            segments.append(seg)
            start = end
    return segments

def split_line_100ft(geom):
    if geom.length < 1:  # Ignore super short/broken lines
        return []
    
    segments = []
    start = 0.0
    while start < geom.length:
        end = min(start + 100, geom.length)
        seg = substring(geom, start, end)
        segments.append(seg)
        start = end
    return segments

split_segments = []

for idx, row in gdf_streets_proj.iterrows():
    parts = explode_and_split(row.geometry)
    for seg in parts:
        split_segments.append({
            "geometry": seg,
            "Model_Score": row.get("Model_Score"),
        })

# Create new GeoDataFrame
gdf_segments = gpd.GeoDataFrame(split_segments, crs=gdf_streets_proj.crs)

'''
endpoints = []

for seg in gdf_segments.geometry:
    if seg is not None and isinstance(seg, LineString):
        end = seg.coords[-1]
        endpoints.append(Point(end))

gdf_endpoints = gpd.GeoDataFrame(geometry=endpoints, crs=gdf_segments.crs)

#Confirm we split to 100 ft

# Check segment lengths
gdf_segments["length_ft"] = gdf_segments.geometry.length

# Print summary
print("Segment Lengths (ft):")
print(gdf_segments["length_ft"].describe())

# Find any segments over 100 ft (should be 0 or just final remainders)
over_100 = gdf_segments[gdf_segments["length_ft"] > 100]
print(f"Segments over 100 ft: {len(over_100)}")
'''
gdf_segments = gdf_segments.to_crs(epsg=4326)

print("Saving")
gdf_segments.to_file("./Geometries/streets_100ft_segments.geojson", driver="GeoJSON")


fig, ax = plt.subplots(figsize=(14, 12))

# Plot segments
gdf_segments.plot(
    ax=ax,
    column="Model_Score",
    cmap="OrRd",
    linewidth=2,
    legend=True,
    legend_kwds={"label": "Model Score per 100 ft", "shrink": 0.6},
    missing_kwds={"color": "lightgrey", "label": "No Data"}
)

ax.set_title("Street Segments per 100 ft")
ax.set_axis_off()
plt.tight_layout()
plt.savefig("Model Score per 100 ft")
plt.show()




