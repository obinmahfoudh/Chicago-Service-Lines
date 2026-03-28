# Config file
import os

# Get the absolute path to the project root
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define Data Paths
# Geometries
CITY_BOUNDS = os.path.join(ROOT_DIR, "data/Geometries/CityBoundaries.csv")
IL_BLOCK_GROUPS = os.path.join(ROOT_DIR, "data/Geometries/IL_BlockGroups/tl_2023_17_bg.shp")
CHICAGO_BLOCK_GROUPS = os.path.join(ROOT_DIR, "outputs/geojsons/chicago_block_groups.geojson")
CHICAGO_BLOCK_GROUPS_ACS_ADI = os.path.join(ROOT_DIR, "outputs/geojsons/chicago_block_groups_with_acs_adi.geojson")

# ACS-ADI
ADI_DATA = os.path.join(ROOT_DIR, "data/IL_2022_ADI_Census_Block_Group_v4_0_1.csv")
ACS_DATA = os.path.join(ROOT_DIR, "data/ACSDT5Y2022.B01001-Data.csv")

# Define Output Paths
GEOJSON_OUT = os.path.join(ROOT_DIR, "outputs/geojsons/")
MAPS_OUT = os.path.join(ROOT_DIR, "outputs/maps/")