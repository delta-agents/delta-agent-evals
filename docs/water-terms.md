# Water terms laypeople read differently

A hydrologist and a passer-by do not mean the same thing by "river basin". In a survey, 34
hydrologists and 119 laypeople in Manchester picked one of four definitions for 12 water terms.
For most terms, fewer than half the laypeople chose the definition the hydrologists chose. With
pictures instead of words, the two groups agreed much more.

For an agent that answers the public, these words are a risk: the answer can be right and still
be read wrong. `delta_agent_evals.Jargon` flags them in each answer, and
[plain_words.py](../examples/plain_words.py) shows it on a hydrologist's answers and plain ones.

| Term | What most hydrologists chose | Hydrologists | Laypeople |
|---|---|---|---|
| river basin | area having a common outlet for its surface runoff | 94% | 13% |
| river | large stream which serves as the natural drainage for a basin | 88% | 15% |
| stream | general term for any body of flowing water | 47% | 18% |
| delta | feature resulting from an alluvial deposit at a river mouth | 61% | 25% |
| groundwater | subsurface water occupying the saturated zone | 79% | 36% |
| discharge | volume of water flowing through a river cross section per unit time | 100% | 45% |
| aquifer | geological formation capable of storing, transmitting and yielding water | 76% | 47% |
| dam | barrier constructed across a valley to store water or raise the water level | 62% | 47% |
| lake | inland body of standing surface water of significant extent | 85% | 53% |
| water table | top surface of the zone of saturation | 82% | 56% |
| downstream | direction in which a fluid is moving | 97% | 58% |
| flood | overflow of water onto lands that are not normally covered by water | 76% | 88% |

Where most laypeople chose something else: a **river** is a "path of fresh water flowing into the
ocean" (71%), a **river basin** the "catchment which a river flows into" (47%), a **delta** a "river
mouth that spreads out a little bit, like the shape of a Greek letter Delta" (35%), and a
**stream** a "small river with water moving fast enough to be visible with the naked eye" (37%).

The survey was in English; Dutch readers may differ. The table above is `WATER_TERMS`, and a test
keeps the two equal.

*From Table B1 of Venhuizen, G. J., Hut, R., Albers, C., Stoof, C. R., & Smeets, I. (2019). Flooded
by jargon: how the interpretation of water-related terms differs between hydrology experts and the
general audience. Hydrology and Earth System Sciences, 23, 393–403.
<https://doi.org/10.5194/hess-23-393-2019>, licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Survey data and code:
<https://doi.org/10.17605/OSF.IO/WK9S6>.*
