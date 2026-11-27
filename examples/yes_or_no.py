"""Yes or no: one contingency table for POD, FAR, CSI and bias, and the Brier score of a probability.

Use case: will four places in Zutphen flood if dike ring 52 breaches? The agent has a hit, a miss,
a false alarm and another hit, and says how sure it is of each answer.
"""

from pydantic import BaseModel
from pydantic_evals import Case, Dataset
from scores.probability import brier_score

from delta_agent_evals import contingency, verify


class Answer(BaseModel):
    floods: bool
    confidence: float | None = None  # 0-1, how sure the agent is of `floods`

    @property
    def p_floods(self) -> float | None:
        """The probability that it floods, from the answer and the agent's confidence in it."""
        return None if self.confidence is None else self.confidence if self.floods else 1 - self.confidence


TRUTH = {"fire station": True, "town hall": True, "school": False, "pumping station": True}
ANSWERS = {  # a hit, a miss, a false alarm and a hit
    "fire station": Answer(floods=True, confidence=0.9),
    "town hall": Answer(floods=False, confidence=0.6),
    "school": Answer(floods=True, confidence=0.7),
    "pumping station": Answer(floods=True, confidence=1.0),
}

dataset = Dataset(
    name="yes_or_no",
    cases=[
        Case(inputs=f"If dike ring 52 breaches, will the {p} in Zutphen flood?", expected_output=Answer(floods=f))
        for p, f in TRUTH.items()
    ],
)


async def agent(question: str) -> Answer:
    return next(a for p, a in ANSWERS.items() if p in question)


report = dataset.evaluate_sync(agent, progress=False)
table = verify("floods", contingency).on(report)
brier = verify("p_floods", brier_score, reference="floods").on(report)
