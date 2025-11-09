import pandas as pd
import geopandas as gpd
from shapely import wkt
import os
import matplotlib.pyplot as plt



# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Read files
print("Loading chicago boundaries")
chicagoBoundaries = pd.read_csv("./Geometries/City_Boundary_20250424.csv")
print("Loading Il block groups")
model =  gpd.read_file("./Geometries/model_scores.geojson")

print("Converting chicago boundaries to pandas geometry")
#Convert multipolygon to wkt
chicagoBoundaries["geometry"] = chicagoBoundaries["the_geom"].apply(wkt.loads)
gdf_chicago = gpd.GeoDataFrame(chicagoBoundaries, geometry="geometry", crs="EPSG:4326")

print("Matching coordinate systems")
model = model.to_crs(gdf_chicago.crs)

if "index_right" in model.columns:
    model = model.drop(columns=["index_right"])


#model_chicago = gpd.sjoin(model, gdf_chicago, how="inner", predicate="within")

model_chicago = model
#model_chicago = model_chicago.to_crs("EPSG:4326")

model_chicago.to_file("./Geometries/model_scores_within.geojson", driver="GeoJSON")

# Plot
fig, ax = plt.subplots(figsize=(10, 10))
model_chicago.plot(
    ax=ax,
    column="CoL",
    cmap="Reds",
    edgecolor="black",
    legend=True,
    missing_kwds={"color": "Blues", "label": "Missing data"}
)

ax.set_title("Cost of Lead Score")
plt.axis("off")
plt.tight_layout()
plt.savefig("CoL_Within_Chicago", dpi= 300, bbox_inches= "tight")
plt.show()

# Plot
fig, ax = plt.subplots(figsize=(10, 10))
model_chicago.plot(
    ax=ax,
    column="avg_LoL",
    cmap="Blues",
    edgecolor="black",
    legend=True,
    missing_kwds={"color": "Blues", "label": "Missing data"}
)

ax.set_title("Likelihood of Lead Score")
plt.axis("off")
plt.tight_layout()
plt.savefig("LoL_Score_Within_Chicago", dpi= 300, bbox_inches= "tight")
plt.show()

# Plot
fig, ax = plt.subplots(figsize=(10, 10))
model_chicago.plot(
    ax=ax,
    column="Model_Score",
    cmap="OrRd",
    edgecolor="black",
    legend=True,
    missing_kwds={"color": "Blues", "label": "Missing data"}
)

ax.set_title("Model Priority Score (CoL x LoL)")
plt.axis("off")
plt.tight_layout()
plt.savefig("Model_Score_Within_Chicago", dpi= 300, bbox_inches= "tight")
plt.show()
