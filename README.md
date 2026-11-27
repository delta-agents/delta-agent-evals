# delta-agent-evals

**How good are an AI agent's answers? Measured with the statistics that water and weather science
use to test their models.**

An agent's answer is treated like a model result, the reference answer like the observation, and any
metric of [scores](https://github.com/nci/scores) compares the two over a dataset of questions run
with [pydantic-evals](https://ai.pydantic.dev/evals/): numbers, yes or no, probabilities, ensembles
and maps per lead time, with ratios pooled over all questions and agents side by side.

**Documentation:** <https://delta-agents.github.io/delta-agent-evals/>

## Installation

```bash
pip install git+https://github.com/delta-agents/delta-agent-evals
```

## Example

```python
from scores.continuous import mae, rmse

from delta_agent_evals import verify

report = dataset.evaluate_sync(agent)        # pydantic-evals: the questions as text, and an agent
errors = verify(None, mae, rmse).on(report)  # any metric of scores on the answers
errors.to_frame()
```

More in [`examples/`](examples/), one question type per file:

| Example | Question | Measures |
|---|---|---|
| [how_deep.py](examples/how_deep.py) | How deep will the water be? | `mae`, `rmse`, `percent_within_x` |
| [will_it_flood.py](examples/will_it_flood.py) | Will it flood? | `contingency`, `brier_score` |
| [dike_breach_map.py](examples/dike_breach_map.py) | Where is the water, every hour? | `fss` and the skillful lead time |
| [water_level_ensemble.py](examples/water_level_ensemble.py) | What will the water level be? | `crps_for_ensemble`, `brier_score_for_ensemble`, `rank_histogram` |
| [better_than_without_tools.py](examples/better_than_without_tools.py) | Better than without tools? | `.skill(...)`, `.paired_bootstrap(...)` |
| [verbal_forecast.py](examples/verbal_forecast.py) | Will it flood, in words? | `PHRASES` and `brier_score` per reader |
| [plain_words.py](examples/plain_words.py) | Do people understand the answer? | `Jargon` |

## Licence

GPL-3.0, [HKV lijn in water](https://www.hkv.nl). The figure in
[docs/probability-phrases.md](docs/probability-phrases.md) is CC BY-NC-ND 4.0 by its authors.
