import config
import matplotlib.pyplot as plt

def plot_scores(cbg, column, cmap = "OrRd", output_path= None):
    """Plot and save score map"""
    fig, ax = plt.subplots(figsize=(10, 10))
    cbg.plot(
        ax=ax,
        column= column,
        cmap= cmap,
        edgecolor="black",
        legend=True,
        missing_kwds={"color": "Blues", "label": "Missing data"}
    )

    ax.set_title(f"{column}")
    plt.axis("off")
    plt.tight_layout()

    if output_path is None:
        output_path = config.MAPS_OUT + f"{column}.png"
    plt.savefig(output_path)
    #plt.show(