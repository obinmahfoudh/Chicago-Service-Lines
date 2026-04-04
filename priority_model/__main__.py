# priority_model/__main__.py
import config
from . import filter_chicago_block_groups
from . import calculate_col
from . import calculate_lol_and_cost
from . import calculate_model_score
from . import plot_scores
from . import create_interactive_map

def main():
    print("Executing Full Priority Model...")
    print("----------------------")

    cbg = filter_chicago_block_groups(config.CITY_BOUNDS, config.IL_BLOCK_GROUPS)
    print("----------------------")

    cbg = calculate_col(config.ACS_DATA,config.ADI_DATA, cbg=cbg)
    print("----------------------")
    plot_scores(cbg, column= "CoL", cmap= "Blues")
    plot_scores(cbg, column= "ACS_Score", cmap= "Blues")
    plot_scores(cbg, column="ADI_Score", cmap= "Blues")

    cbg = calculate_lol_and_cost(config.SERVICE_LINES, cbg= cbg)
    print("----------------------")
    plot_scores(cbg, column= "LoL")

    cbg = calculate_model_score(cbg= cbg, save_file=True)
    print("----------------------")
    plot_scores(cbg, column="Model_Score")

    create_interactive_map(cbg)

if __name__ == "__main__":
    main()