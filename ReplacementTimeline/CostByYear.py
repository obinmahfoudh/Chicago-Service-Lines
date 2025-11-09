import geopandas as gpd
import matplotlib.pyplot as plt
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors




# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

cbg = gpd.read_file("./Geometries/model_scores.geojson")

cbg = cbg.sort_values(by="Model_Score", ascending=False).reset_index(drop=True)

ANNUAL_BUDGET = 53000000
current_year = 2025

cbg["Replacement_Year"] = None
remaining = cbg.copy()
#print(cbg["Min_Cost_Entire"].sum())

total_cost= 0

while not remaining.empty:
    budget = ANNUAL_BUDGET
    year_blocks = []

    for idx, row in remaining.iterrows():
        cost = row["Min_Cost_Entire"]
        if cost <= budget:
            year_blocks.append(idx)
            budget -= cost
            total_cost += cost

    # Assign year to selected blocks
    cbg.loc[year_blocks, "Replacement_Year"] = current_year
    # Remove assigned blocks from remaining
    remaining = remaining.drop(year_blocks)
    current_year += 1

print(total_cost)
# Filter only blocks with a year assigned
cbg = cbg[cbg["Replacement_Year"].notna()]
cbg["Replacement_Year"] = cbg["Replacement_Year"].astype(int)

# Setup animation parameters
years = sorted(cbg["Replacement_Year"].unique())
cmap = plt.get_cmap("viridis", len(years))
norm = mcolors.BoundaryNorm(boundaries=[y - 0.5 for y in years] + [years[-1] + 0.5], ncolors=len(years))

fig, ax = plt.subplots(figsize=(12, 12))

def update(year_idx):
    ax.clear()
    current_year = years[year_idx]
    
    # Filter blocks up to this year
    visible_blocks = cbg[cbg["Replacement_Year"] <= current_year]
    
    visible_blocks.plot(
        ax=ax,
        column="Replacement_Year",
        cmap=cmap,
        edgecolor="black",
        linewidth=0.2,
        norm=norm
    )
    
    ax.set_title(f"Lead Service Line Replacement Plan\nUp to Year {current_year}", fontsize=30)
    plt.tight_layout()
    ax.axis("off")

# Build the animation
anim = FuncAnimation(fig, update, frames=len(years), repeat=False)

# Save as gif or mp4
anim.save("replacement_timeline_entire.gif", writer="pillow", fps=5)
