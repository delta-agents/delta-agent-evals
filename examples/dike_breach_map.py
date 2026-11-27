"""Where is the water after a dike breach? A map per hour, verified with the Fractions Skill Score.

A polder of 3 x 10 pixels of 25 m with the breach on its west side. In the reference, a model run,
the water covers two more pixels eastward every hour. The agent gets the width right but places the
water one pixel further east every hour. Small enough to count by hand: see tests/test_examples.py.
"""

import numpy as np
from pydantic_evals import Case, Dataset

from delta_agent_evals import Grid, each, fss, verify

COLUMNS = np.arange(10)


def flood(shift: int = 0) -> Grid:
    """1 m of water on the 2h columns nearest the breach after h hours, moved `shift` columns east per hour."""
    wet = [(COLUMNS >= shift * (h - 1)) & (COLUMNS < shift * (h - 1) + 2 * h) for h in (1, 2, 3)]
    return Grid(lead_time=[60, 120, 180], data=np.stack([np.tile(w, (3, 1)) for w in wet]).astype(float))


dataset = Dataset(
    name="dike_breach",
    cases=[
        Case(
            inputs="The dike breaches at the pumping station at 14:00. "
            "Where is the polder wet, on a 25 m grid, at 15:00, 16:00 and 17:00?",
            expected_output=flood(),
        )
    ],
)


async def agent(question: str) -> Grid:
    return flood(shift=1)


report = dataset.evaluate_sync(agent, progress=False)
maps = verify(None, fss, event_threshold=0.5, window_size=each(1, 3)).on(report)
