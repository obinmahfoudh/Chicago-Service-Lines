import pandas as pd
import os
from shapely.geometry import Point
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


print("Loading street data")
street_data = pd.read_csv("./Streets/transportation_20250417.csv")
street_data['geometry'] = street_data['the_geom'].apply(wkt.loads)
gdf_streets = gpd.GeoDataFrame(street_data, geometry='geometry', crs="EPSG:4326")

print("Loading service line data")
service_line = pd.read_csv("./service_line_geocoded_fixed_final.csv")  

# Convert Geodata string to Point geometry
def geodata_to_point(geodata):
    try:
        lon, lat = map(float, geodata.split(','))
        return Point(lon, lat)
    except:
        return None

print("Converting geodata to points")
service_line['geometry'] = service_line['lat_long'].apply(geodata_to_point)
gdf_service = gpd.GeoDataFrame(service_line, geometry='geometry', crs="EPSG:4326").dropna(subset=['geometry'])

# Change crs to better measure distances
#print("Reprojecting to EPSG:26971")
gdf_service = gdf_service.to_crs(epsg=26971)
gdf_streets = gdf_streets.to_crs(epsg=26971)

print("Making full street names")
gdf_streets["FULL_STREET"] = (
    gdf_streets["PRE_DIR"].fillna('') + " " +
    gdf_streets["STREET_NAM"].fillna('') + " " +
    gdf_streets["STREET_TYP"].fillna('')
).str.strip().str.upper()

# Matching service lines to steets
print("Matching service lines to nearest street segments")
matched = gpd.sjoin_nearest(
    gdf_service,
    gdf_streets[['geometry', 'FULL_STREET']],
    how='left',
    distance_col='distance_to_street'
)

# Label risky service lines
print("Flagging risky service lines")
def is_risky(row):
    return row.get("Classification for Entire Serivice Line", "") in ["L", "GRR", "U"]


matched["is_risky"] = matched.apply(is_risky, axis=1)

print("Number of risky service lines:", matched["is_risky"].sum())
#print("Total service lines matched:", len(matched))

# Count risky service lines
print("Counting risky lines per street")
risky_counts = matched[matched['is_risky']].groupby("FULL_STREET").size().reset_index(name="risky_count")



# Group streets and add lengths
print("Merging street segments by name and summing lengths")
gdf_streets["length"] = gdf_streets.geometry.length
grouped_streets = gdf_streets.dissolve(by='FULL_STREET', aggfunc={'length': 'sum'}).reset_index()
risky_counts = matched[matched['is_risky']].groupby("FULL_STREET").size().reset_index(name="risky_count")


# Normalize 
print("Merging risky counts and computing normalized risk")
grouped_streets = grouped_streets.merge(risky_counts, on="FULL_STREET", how="left")
grouped_streets["risky_count"] = grouped_streets["risky_count"].fillna(0)
grouped_streets["risk_score"] = grouped_streets["risky_count"] / (grouped_streets["length"])

print(grouped_streets[['FULL_STREET', 'risky_count', 'length','risk_score']].sort_values('risk_score', ascending=False).head(10))

# Plotting
# Filter risky points only
risky_points = matched[matched["is_risky"] == True]

# Get top 10 riskiest streets by risky_count
top10 = grouped_streets.sort_values("risky_count", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(14, 12))

# Base: all streets colored by risk score
grouped_streets.plot(
    column="risky_count",
    ax=ax,
    cmap="OrRd",
    legend=True,
    linewidth=2,
    legend_kwds={'label': "Risky Lines per km"}
)

# Highlight top 10 streets with a black border
top10.plot(
    ax=ax,
    facecolor='none',
    edgecolor='black',
    linewidth=2.5,
    label='Top 10 Riskiest Streets'
)

# Optional: label top 10 streets with street names
for _, row in top10.iterrows():
    midpoint = row.geometry.interpolate(0.9, normalized=True)
    ax.text(midpoint.x, midpoint.y, row['FULL_STREET'], fontsize=8, color='black')

# Reuse the FULL_STREET + length data to get a nice street base
fig, ax = plt.subplots(figsize=(14, 12))

# Streets
grouped_streets.plot(
    ax=ax,
    color='lightgray',
    linewidth=1,
    label='Street Segments'
)

# Overlay on street segments
matched["risk_status"] = matched["is_risky"].map({True: "Risky", False: "Not Risky"})

matched.plot(
    ax=ax,
    column="risk_status",
    categorical=True,
    legend=True,
    cmap="coolwarm",  # Red/blue
    markersize=5,
    alpha=0.7,
)

plt.title("All Service Line Points by Risk on Street Network")
plt.axis("off")
plt.tight_layout()
plt.savefig("map_all_points_over_streets.png", dpi=300)
plt.show()


print("Done!")
