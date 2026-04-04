"""
This module creates an interactive map of chicagos block groups with detailed information provided on hover for each one

Inputs:
    - Chicago Block Groups with model scores 

Outputs: 
    - Returns: Interactive html page with block group and there respective data
"""
import config
import geopandas as gpd
import folium
import branca.colormap as cm

def create_interactive_map(gdf=None, gdf_path=None, output_path=config.MAPS_OUT + "chicago_interactive_map.html"):
    print("Creating interactive model map")
    # Load data
    if gdf is not None:
        print("Using provided GeoDataFrame") 
    elif gdf_path is not None:
        gdf = gpd.read_file(gdf_path)
    else:
        raise ValueError('Must provide either \'gdf\' (GeoDataFrame) or a valid \'gdf_path\' (string).')

    # Set CRS
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # Create the Color Scale
    colormap = cm.linear.YlOrRd_09.scale(gdf["Model_Score"].min(), gdf["Model_Score"].max())
    colormap.caption = "Priority Model Score"

    # Initialize Map to Chicago coords
    m = folium.Map(location=[41.8781, -87.6298], zoom_start=11, tiles="cartodbpositron")

    # Choose columns wanted
    columns = ["GEOID", "CoL", "LoL", "Model_Score"]
    aliases = ["Block Group ID:", "Cost of Living:", "Likelihood of Lead:", "Final Priority Score:"]
    
    folium.GeoJson(
        gdf,
        name="Chicago Priority Model",
        style_function=lambda x: {
            "fillColor": colormap(x["properties"]["Model_Score"]),
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=columns,
            aliases= aliases,
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """
        ),
        popup=folium.GeoJsonPopup(
            fields=columns,
            aliases= aliases,
            localize=True,
            labels=True,
            style="background-color: white; color: #333; font-family: sans-serif; font-size: 12px; padding: 10px;"
        )
    ).add_to(m)

    # Add legend
    colormap.add_to(m)
    m.save(output_path)
    print(f"Map successfully saved to {output_path}")