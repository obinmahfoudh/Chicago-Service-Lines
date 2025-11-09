Chicago has more lead service lines than any other U.S. city (over 400,000) posing a major public health concern. This project prioritizes replacement efforts using a block group–level risk model that combines demographic vulnerability (social cost of lead) with infrastructure data (likelihood of lead)

# Priority Model

The prioritization method is adapted from a model used by Safe Water Engineering in Washington, D.C.. Replacement priorities are assessed at the block group level, which typically includes between 600 and 3,000 residents. Each block group is evaluated using two key metrics:

Cost of Lead (CoL): A social harm score that reflects the potential impact of lead exposure on vulnerable populations. It incorporates the Area Deprivation Index (ADI), which is a composite measure of socioeconomic disadvantage, and the number of children under 5, who are most at risk from lead exposure
Likelihood of Lead (LoL): The average number of service lines within the block group that are suspected to require replacement.
Each score is normalized on a scale of 1 to 10. By multiplying CoL and LoL, we generate a composite priority score ranging from 0 to 100, identifying which block groups should be prioritized for service line replacement.

CoL Score
CoL = 0.5 * ADI Score + 0.5 * Children under 5 score

Children under 5 score
50+ children:  10
11-50 children: 5
1-10 children:   3
No children:      1 

LoL score
Lead and galvanized lines: 10.
Unknowns: 5
Non-Lead: 0

Model score = CoL * LoL

# Timeline

The timeline was made based off of a budget of $53 million according to this https://ilenviro.org/iec-2025-chicago-budget-analysis/. The estimated cost of replacement for a service line was assumed to be 16,000, the lower of the estimated ranged cost of 16,000-30,000, based off of the city of Chicagos website https://www.leadsafechicago.org/lead-service-line-replacement.  
Two timelines were made one assuming full replacement of both service lines even if only one side is lead or galvanized needing replacement and the other assuming we fix only the lines needing replacement so those made of lead or galvanized needing replacement. The blocks were sorted according to the priority model made above and for each year we just kept going through the blocks replacing service lines until the budget could not replace another full one, at that point we go to the next year and replenish the budget repeating the steps from before. Of course this is not the best way to do this and there are methods to better optimize replacement to utilize the full budget, but due to the nature of government and the above mentioned leniencies in cost of replacement the model still serves as a decent visualization, although not optimized. The overall metrics and the replacement timeline gif for partial replacement are shown below.

<img width="320" height="78" alt="image" src="https://github.com/user-attachments/assets/b9774a98-09ff-42b4-9c50-05a16a6e30bd" />

![replacement_gif](Images&MapViews/replacement_timeline_partial.gif)
