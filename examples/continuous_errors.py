"""Continuous errors: MAE, RMSE and how often an answer is within a tolerance.

Use case: how deep will the water be at four places in Zutphen if dike ring 52 breaches? The
agent does not answer for the last place; that answer is left out and counted as missing.
"""

from pydantic_evals import Case, Dataset
from scores.continuous import mae, percent_within_x, rmse

from delta_agent_evals import each, verify

TRUTH = {"fire station": 1.0, "town hall": 2.0, "school": 0.0, "pumping station": 4.0}
ANSWERS = {"fire station": 1.05, "town hall": 1.8, "school": 0.0, "pumping station": None}

dataset = Dataset(
    name="continuous_errors",
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
