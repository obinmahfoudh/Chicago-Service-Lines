import config
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely import wkt
from shapely import LineString
from shapely.ops import substring

def project_model_to_street(model_path = None, model= None):
    print("Projecting model to streets")
    # Read data
    if model is not None:
       print("Using provided GeoDataFrame") 
    elif model_path is not None:
        model = gpd.read_file(model_path)
    else:
        raise ValueError('Must provide either \'model\' (GeoDataFrame) or a valid \'model_path\' (string).')
    
    print("Loading street data")
    street_data = pd.read_csv(config.CHICAGO_STREETS)
    street_data['geometry'] = street_data['the_geom'].apply(wkt.loads)
    
    gdf_streets = gpd.GeoDataFrame(street_data, geometry='geometry', crs="EPSG:4326")
    # Exclude highways and other interstate roads
    #exclude_types = ['EXPY', 'ER', 'XR', 'PKWY', 'RL', 'SQ', 'SR', 'HWY', 'TOLL', 'PLZ', 'ORD', 'ROW']
    #gdf_streets = gdf_streets[~gdf_streets["STREET_TYP"].isin(exclude_types) | gdf_streets["STREET_TYP"].isna()]

    print("Performing spatial join") 
    # Project block group model to street crs to do a spatial join
    model = model.to_crs(gdf_streets.crs)
    segments_with_score = gpd.sjoin(
        gdf_streets,
        model[["GEOID", "Model_Score", "geometry"]],
        how="left",
        predicate="intersects"
    )
    print("Calculating average score for each street segment")
    # Calculate mean score to get avaerage for each street segment
    mean_scores = segments_with_score.groupby('OBJECTID')['Model_Score'].mean().reset_index()
    # Merge back to streeg segment data
    gdf_streets = gdf_streets.merge(mean_scores, on='OBJECTID', how='left')

    # Save as geojson
    gdf_streets.to_file(config.GEOJSON_OUT + "street_model_scores.geojson", driver="GeoJSON")
    
    # Plot figure
    fig, ax = plt.subplots(figsize=(14, 12))
    gdf_streets.plot(
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
    plt.savefig(config.MAPS_OUT + "ModelPerStreetSegments.png")
    
    
def main():
    print("Running ProjectModelToStreets.py")
    project_model_to_street(model_path=config.MODEL)

if __name__ == "__main__":
    main()
