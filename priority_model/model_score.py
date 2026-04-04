"""
This Module uses the CoL and LoL scores to calculate a final priority model score.

Inputs:
    - Chicago Block Groups (With LoL and CoL score columns)

Outputs:
    - GeoJSON: model_scores.geojson
    - Visualization: chicago_block_groups.png
"""

import config
import geopandas as gpd
from . import visualization

def calculate_model_score(cbg_path= None, cbg= None, save_file = False):
    """Calculates model score using formula model_score = CoL * LoL"""    

    if cbg is not None:
       print("Using provided GeoDataFrame") 
    elif cbg_path is not None:
        cbg = gpd.read_file(cbg_path)
    else:
        raise ValueError('Must provide either \'cbg\' (GeoDataFrame) or a valid \'cbg_path\' (string).')

    print("Calculating priority model scores")
    cbg["Model_Score"] = cbg["CoL"] * cbg["LoL"]
    if save_file:
        print("Saving file")
        cbg.to_file(config.GEOJSON_OUT + "model_scores.geojson",driver= "GeoJSON")

    return cbg

def main():
    cbg = calculate_model_score(
        cbg_path= config.GEOJSON_OUT + "chicago_block_groups_with_col_lol_costs.geojson",
        save_file=True
    )

    visualization.plot_scores(cbg, column=['Model_Score'])

if __name__ == "__main__":
    main()