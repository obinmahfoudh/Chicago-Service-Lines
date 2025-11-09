import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
from shapely import wkt
from shapely import LineString
from shapely.ops import substring


# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


model =  gpd.read_file("./Geometries/model_scores.geojson")


print("Loading street data")
street_data = pd.read_csv("../Streets/transportation_20250417.csv")
street_data['geometry'] = street_data['the_geom'].apply(wkt.loads)

gdf_streets = gpd.GeoDataFrame(street_data, geometry='geometry', crs="EPSG:4326")

exclude_types = ['EXPY', 'ER', 'XR', 'PKWY', 'RL', 'SQ', 'SR', 'HWY', 'TOLL', 'PLZ', 'ORD', 'ROW']
gdf_streets = gdf_streets[~gdf_streets["STREET_TYP"].isin(exclude_types) | gdf_streets["STREET_TYP"].isna()]


model = model.to_crs(gdf_streets.crs)

segments_with_score = gpd.sjoin(
    gdf_streets,
    model[["GEOID", "Model_Score", "geometry"]],
    how="left",
    predicate="intersects"
)

#print(segments_with_score["Model_Score"])
segments_with_score.to_file("./Geometries/street_model_scores.geojson", driver="GeoJSON")


fig, ax = plt.subplots(figsize=(14, 12))
segments_with_score.plot(
    ax=ax,
    column="Model_Score",
    cmap="OrRd",
    linewidth=2,
    legend=True,
    legend_kwds={"label": "Block-Level Model Score", "shrink": 0.6},
    missing_kwds={"color": "lightgrey", "label": "No Data"}
)
plt.title("Street Segments Colored by Block Group Model Score")
plt.axis("off")
plt.tight_layout()
plt.savefig("ModelPerStreetSegments")
plt.show()

'''
filtered_opp = segments_with_score[segments_with_score["STREET_TYP"].isin(exclude_types) | segments_with_score["STREET_TYP"].isna()]
filtered_opp.plot(figsize=(12, 10), color='red', linewidth=2)
plt.title("Excluded Streets (Likely Highways)")
plt.axis('off')
plt.tight_layout()
plt.show()
'''

