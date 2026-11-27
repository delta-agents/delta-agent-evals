"""Will it flood? An agent that answers in words, scored the way people read them.

"Likely" is 57% to a cautious reader and 91% to a bold one (docs/probability-phrases.md). Each
word becomes the low, mean and high reading of that study, and the Brier score shows what the
same answers are worth to each reader.
"""

from pydantic import BaseModel
from pydantic_evals import Case, Dataset
from scores.probability import brier_score

from delta_agent_evals import PHRASES, verify


class Answer(BaseModel):
    floods: bool | None = None
    chance: str | None = None  # the agent's word for how likely it is to flood


TRUTH = {"fire station": True, "town hall": True, "school": False, "pumping station": True, "power station": True}
WORDS = {  # "fifty-fifty" is not in the study, so that answer counts as missing
    "fire station": "likely",
    "town hall": "possible",
    "school": "unlikely",
    "pumping station": "very likely",
    "power station": "fifty-fifty",
}

dataset = Dataset(
    name="verbal_forecast",
    cases=[
        Case(
            inputs=f"If dike ring 52 breaches, how likely is the {p} in Zutphen to flood?",
            expected_output=Answer(floods=f),
        )
        for p, f in TRUTH.items()
    ],
)


async def agent(question: str) -> Answer:
    return Answer(chance=next(w for p, w in WORDS.items() if p in question))


report = dataset.evaluate_sync(agent, progress=False)
as_read = verify(lambda a: PHRASES.get(a.chance), brier_score, reference="floods", preserve_dims=["reading"])
brier = as_read.on(report)
