"""What will the water level be? An agent that answers with an ensemble, and any `scores` metric for ensembles."""

from pydantic_evals import Case, Dataset
from scores.probability import brier_score_for_ensemble, crps_for_ensemble, rank_histogram

from delta_agent_evals import Ensemble, Series, verify

ALARM = 1.5  # m
TIMES = ["00:00", "06:00", "12:00"]
MEMBERS = [[1.0, 1.0, 2.0, 2.0], [1.0, 1.0, 1.0, 2.0], [2.0, 2.0, 2.0, 2.0]]
OBSERVED = [1.8, 1.2, 1.2]

dataset = Dataset(
    name="water_level",
    cases=[
        Case(
            inputs=f"What will the water level at the Zutphen gauge be 6 hours after {t}? Give four members.",
            expected_output=Series(lead_time=[6], values=[o]),
        )
        for t, o in zip(TIMES, OBSERVED)
    ],
)


async def agent(question: str) -> Ensemble:
    return Ensemble(lead_time=[6], members=[MEMBERS[next(i for i, t in enumerate(TIMES) if t in question)]])


report = dataset.evaluate_sync(agent, progress=False)
crps = verify(None, crps_for_ensemble, ensemble_member_dim="member", method="fair").on(report)
above_alarm = verify(None, brier_score_for_ensemble, ensemble_member_dim="member", event_thresholds=ALARM)
brier = above_alarm.on(report)
ranks = verify(None, rank_histogram, ens_member_dim="member").on(report)
