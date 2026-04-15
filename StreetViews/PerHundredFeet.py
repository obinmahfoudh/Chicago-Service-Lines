import config
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import substring


def model_to_hundred_feet(model_path=None, model=None):

    if model is not None:
       print("Using provided GeoDataFrame") 
    elif model_path is not None:
        model = gpd.read_file(model_path)
    else:
        raise ValueError('Must provide either \'model\' (GeoDataFrame) or a valid \'model_path\' (string).')
    
    # Project to Illinois State Plane (Meters/Feet)
    gdf_streets_proj = model.to_crs(epsg=3435)
    
    split_data = []

    for idx, row in gdf_streets_proj.iterrows():
        geom = row.geometry
        
        # Explode MultiLineStrings into a list of LineStrings
        if isinstance(geom, MultiLineString):
            lines = list(geom.geoms)
        elif isinstance(geom, LineString):
            lines = [geom]
        else:
            continue

        # Split each LineString into 100ft chunks
        for line in lines:
            length = line.length

            start = 0.0
            while start < length:
                end = min(start + 100.0, length)
                
                # normalized=False tells shapely to use feet, not %
                seg = substring(line, start, end, normalized=False)
                
                if not seg.is_empty:
                    split_data.append({
                        "geometry": seg,
                        "Model_Score": row.get("Model_Score"),
                        "OBJECTID": row.get("OBJECTID") 
                    })
                start = end

    # Create the new GeoDataFrame
    gdf_segments = gpd.GeoDataFrame(split_data, crs=gdf_streets_proj.crs)
    
    # Check lengths now
    gdf_segments["length_ft"] = gdf_segments.geometry.length
    print(f"Summary of lengths:\n{gdf_segments['length_ft'].describe()}")
    
    over_100 = gdf_segments[gdf_segments["length_ft"] > 100.001] 
    print(f"Segments over 100 ft: {len(over_100)}")

    print("Saving")
    print(len(gdf_segments))
    gdf_segments.to_file(config.GEOJSON_OUT + "streets_100ft_segments.geojson", driver="GeoJSON")
    
    
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
    plt.savefig(config.MAPS_OUT + "Model Score per 100 ft.png")
    plt.show()
    
def main():
    model_to_hundred_feet(model_path= config.STREET_MODEL)

if __name__ == "__main__":
    main()