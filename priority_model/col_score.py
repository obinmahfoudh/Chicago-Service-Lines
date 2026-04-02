"""
This Module calculates a Cost of Living score for block groups in Chicago based off of Census ADI data and the number of children under 5

ACS score is determined using the ACS B01001 (Census) table to find the number of children under 5 and adding that data to our chicago block group data 
Creates bins for number of children under 5 to calculate a score for each block group. 

ADI Score uses the Neighborhood Atlas's block group ADI data to attatch scores to our chicago block group data
Uses state ADI scores 

COL Score is a score of 1-10 determining the vulnerability of the population with 10 being a highly vulnerable population.
CoL = 0.5 * ACS_Score + 0.5 * ADI_Score

Inputs:
    - Chicago Block Groups 
    - IL ACS Data (Cook and Dupage Counties): 'CSDT5Y2022.B01001-Data.csv
    - IL ADI Data: 'IL_2022_ADI_Census_Block_Group_v4_0_1' 

Outputs: 
    - Returns: Geodata Frame (Chicago block groups with COL score) 
    - Visualization: 'COL_Score.png'
"""

import config
from . import visualization
import geopandas as gpd
import pandas as pd

def calculate_col(acs_path, adi_path, cbg_path= None, cbg= None):
    """
    Calculates a COL score from the ACS and ADI scores
    COL = 0.5 * ACS_SCORE + 0.5 * ADI_SCORE

    Args:
        Either:
            cbg_path (str): File path to chicago block group data
            cbg (GeoDataFrame): pre-loaded GeoDataFrame
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups with ADI data
    """
    print("Calculating CoL Score")
    # Read data
    if cbg is not None:
       print("Using provided GeoDataFrame") 
    elif cbg_path is not None:
        cbg = gpd.read_file(cbg_path)
    else:
        raise ValueError('Must provide either \'cbg\' (GeoDataFrame) or a valid \'cbg_path\' (string).')


    cbg = merge_acs(acs_path, cbg= cbg)
    cbg = merge_adi(adi_path, cbg= cbg)

    cbg["CoL"] = 0.5 * cbg["ADI_Score"] + 0.5 * cbg["ACS_Score"]

    return cbg

def merge_acs(acs_path, cbg_path= None, cbg= None):

    """
    Calculates an ACS score for each block group in Chicago based on the number of children under 5 within that block group 
    ACS score metrics taken from safe water engineering

    Args:
        acs_path (str): File path to ACS data
        cbg_path (str): File path to chicago block group data
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups with acs data
    """

    print("Merging ACS scores into dataframe")

    # Read data
    acs_data = pd.read_csv(acs_path)
    if cbg is not None:
       print("Using provided GeoDataFrame") 
    elif cbg_path is not None:
        cbg = gpd.read_file(cbg_path)
    else:
        raise ValueError('Must provide either \'cbg\' (GeoDataFrame) or a valid \'cbg_path\' (string).')

    if 'ACS_Score' in cbg.columns:
        print("ADI data already exists in this GeoDataFrame. Skipping merge.")
        return cbg

    print("Counting children under 5")
    # Male <5
    acs_data["B01001_003E"] = pd.to_numeric(acs_data["B01001_003E"], errors='coerce')  
    # Female <5
    acs_data["B01001_027E"] = pd.to_numeric(acs_data["B01001_027E"], errors='coerce')  
    acs_data["children_under_5"] = acs_data["B01001_003E"] + acs_data["B01001_027E"]

    print("Scoring block groups")
    def scoreACS(number):
        """Set ACS score for block group depending on number of children under 5 present"""
        if number == 0:
            return 1
        elif number <= 10:
            return 3
        elif number <= 50:
            return 5
        else:
            return 10

    # Apply score
    acs_data["ACS_Score"] = acs_data["children_under_5"].apply(scoreACS)

    # Rename block group column to match ACS data column name
    acs_data.rename(columns={"GEO_ID": "GEOIDFQ"}, inplace= True)
    print("Merging data to dataframe")
    # Merge
    cbg = cbg.merge(
        acs_data[["GEOIDFQ", "ACS_Score"]],
        on="GEOIDFQ",
        how="left"
    )

    print("ACS Score distribution")
    print(f"Total block groups: {len(cbg)}")
    print(cbg["ACS_Score"].value_counts().sort_index())

    return cbg   

def merge_adi(adi_path, cbg_path= None, cbg= None):
    """
    Gets ADI score for each block group from census data and merge that into the chicago block group dataframe
    Uses state rank to better capture chicago compared to other block groups in the state.

    Args:
        adi_path (str): File path to ADI data
        cbg_path (str): File path to chicago block group data
    
    Returns:
        geojson: A geojson in EPSG:4326 containing chicago block groups with ADI data
    """

    print("Merging ADI score into dataframe")

    # Read data
    adi = pd.read_csv(adi_path)
    if cbg is not None:
       print("Using provided GeoDataFrame") 
    elif cbg_path is not None:
        cbg = gpd.read_file(cbg_path)
    else:
        raise ValueError('Must provide either \'cbg\' (GeoDataFrame) or a valid \'cbg_path\' (string).')

    if 'ADI_Score' in cbg.columns:
        print("ADI data already exists in this GeoDataFrame. Skipping merge.")
        return cbg
        
    # Change column name to merge easier
    adi = adi.rename(columns={"FIPS": "GEOID"})
    # Read as string or it gets funky
    cbg["GEOID"] = cbg["GEOID"].astype(str)
    adi["GEOID"] = adi["GEOID"].astype(str)

    # For block groups without score set to 5 
    def clean_adi_rank(val):
        try:
            return int(val)
        except:
            return 5

    print("Cleaning data (filling empty scores)")
    adi["ADI_Score"] = adi["ADI_STATERNK"].apply(clean_adi_rank)

    print("Merging ADI score to dataframe")
    cbg = cbg.merge(
        adi[["GEOID", "ADI_Score"]],
        on="GEOID",
        how="left"
    )

    return cbg

def main():
    print("Running calculate_col.py")
    cbg = calculate_col(config.ACS_DATA, config.ADI_DATA, config.CHICAGO_BLOCK_GROUPS)

    print("Saving file to " + config.GEOJSON_OUT)
    cbg.to_file(config.GEOJSON_OUT + "chicago_block_groups_with_col.geojson", driver="GeoJSON")

    visualization.plot_scores(cbg, column= "CoL", cmap= "Blues")

if __name__ == "__main__":
    main()
