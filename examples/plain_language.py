"""Plain language: water terms that most laypeople read differently from hydrologists.

Use case: the same three answers by a hydrologist and in plain words. "Discharge" is the volume of
water per second through a river's cross section to every hydrologist, and to 45% of laypeople
(docs/water-terms.md). `Jargon` flags such terms in each answer; it needs no reference answer, so
it also works as an online evaluator on live traffic.
"""

from pydantic_evals import Case, Dataset

from delta_agent_evals import Jargon

ANSWERS = {
    "How much water will the IJssel carry at Zutphen tomorrow?": (
        "The discharge at Zutphen peaks at 1,200 m3/s tomorrow afternoon.",
        "Tomorrow afternoon about 1,200 cubic metres of water per second flow past Zutphen.",
    ),
    "Where does the water go if dike ring 52 breaches?": (
        "It spreads downstream over the river basin.",
        "It flows north-west over the polder, to the lowest land first.",
    ),
    "Will my cellar in Zutphen get wet?": (
        "The groundwater rises to 0.5 m below the surface.",
        "The water in the ground rises to half a metre below the street, so a deep cellar may get wet.",
    ),
}

dataset = Dataset(name="plain_language", cases=[Case(inputs=q) for q in ANSWERS], evaluators=[Jargon()])


async def hydrologist(question: str) -> str:
    return ANSWERS[question][0]


async def plain(question: str) -> str:
    return ANSWERS[question][1]


reports = {
    name: dataset.evaluate_sync(agent, progress=False)
    for name, agent in [("hydrologist", hydrologist), ("plain", plain)]
}
