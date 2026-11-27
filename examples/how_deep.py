"""How deep will the water be? Errors of a number in the answer, and how often it is within a tolerance."""

from pydantic_evals import Case, Dataset
from scores.continuous import mae, percent_within_x, rmse

from delta_agent_evals import each, verify

TRUTH = {"fire station": 1.0, "town hall": 2.0, "school": 0.0, "pumping station": 4.0}
ANSWERS = {"fire station": 1.05, "town hall": 1.8, "school": 0.0, "pumping station": None}  # no answer for the last

dataset = Dataset(
    name="how_deep",
    cases=[
        Case(inputs=f"If dike ring 52 breaches, how deep is the water at the {p} in Zutphen?", expected_output=d)
        for p, d in TRUTH.items()
    ],
)


async def agent(question: str) -> float | None:
    return next(d for p, d in ANSWERS.items() if p in question)


report = dataset.evaluate_sync(agent, progress=False)
errors = verify(None, mae, rmse).on(report)
hits = verify(None, percent_within_x, threshold=each(0.1, 0.25, 0.5)).on(report)
