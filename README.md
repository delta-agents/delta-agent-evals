# delta-agent-evals

**delta-agent-evals** tests [Delta Agents](https://delta-agents.nl) the way we have tested
forecasts for years. The agent's answer is the forecast, the reference answer is the observation,
and every measure of [scores](https://github.com/nci/scores) is there to compare them.

```python
from scores.continuous import mae, rmse
from delta_agent_evals import verify

report = dataset.evaluate_sync(agent)  # a pydantic-evals Dataset of questions as text
verify("max_depth_m", mae, rmse).on(report)
```

That is all there is to it. [pydantic-evals](https://ai.pydantic.dev/evals/) runs the questions,
`verify` turns the answers into arrays, and any `scores` metric does the rest: errors, hits and
false alarms, Brier and CRPS, the Fractions Skill Score of a map.

## Contents

- [Installation](#installation)
- [Examples](#examples)
- [How it works](#how-it-works)
- [Three things to remember](#three-things-to-remember)
- [Development](#development)
- [Licence](#licence)

## Installation

```bash
pip install git+https://github.com/delta-agents/delta-agent-evals
pip install "delta-agent-evals[plot] @ git+https://github.com/delta-agents/delta-agent-evals"  # with plots
```

## Examples

Each example is a few questions, an agent with known answers, and one line of `verify`. Run them
with `uv run examples/how_deep.py`.

| Example | The question | Measured with |
|---|---|---|
| [how_deep.py](examples/how_deep.py) | How deep is the water at the fire station? | `mae`, `rmse`, and `percent_within_x` per tolerance |
| [will_it_flood.py](examples/will_it_flood.py) | Will the fire station flood? | `contingency` (POD, FAR, CSI), `brier_score` of the probability the agent gives |
| [dike_breach_map.py](examples/dike_breach_map.py) | Where is the polder wet, every hour? | `fss` and the skillful lead time, per scale |
| [water_level_ensemble.py](examples/water_level_ensemble.py) | What will the water level be in 6 hours? | `crps_for_ensemble`, `rank_histogram`, a Brier score of your own |
| [verbal_forecast.py](examples/verbal_forecast.py) | How likely is the fire station to flood? (in words) | `PHRASES` and `brier_score` per reader |
| [better_than_without_tools.py](examples/better_than_without_tools.py) | Is the agent better than without tools? | `.skill(...)` and `.paired_bootstrap(...)` |

The dike breach in a few lines:

```python
from delta_agent_evals import each, fss, verify

maps = verify(None, fss, event_threshold=0.5, window_size=each(1, 3)).on(report)
maps["skillful_lead_time"]  # 120 min per 25 m pixel, 180 min at 75 m
```

The agent places the water a little further east every hour. Per pixel its map is useful for two
hours; looked at 75 m wide, for all three.

## How it works

- **Answers become arrays.** `verify("max_depth_m", ...)` takes that field from every answer and
  every reference answer: a number, a yes/no as 1/0, or anything with `to_xarray()`, such as a
  `Grid` (a map per lead time) or an `Ensemble`. The field can also be a function of the answer,
  e.g. `lambda a: CLASSES.index(a.impact)` for ordered classes.
- **One question, many runs.** The answers get a `question` and a `run` dimension. Run the dataset
  with `evaluate(repeat=5)` and the runs are an ensemble:
  `verify("max_depth_m", crps_for_ensemble, ensemble_member_dim="run")`.
- **A missing answer is NaN**, and `scores` leaves it out. The result says how many there were.
- **Any metric.** A metric is any function `(fcst, obs, **options)`, so everything in `scores`
  works as it is, and so does a function of your own. Options go to every metric; an option given
  as `each(...)` is swept and becomes a coordinate.
- **Several agents side by side.** `.on(agent=report, without_tools=base)` adds an `agent`
  coordinate; `.skill("without_tools")` gives 1 - score / score of the reference.
- **One result.** A `Verification` is an xarray Dataset with `.to_frame()` for a tidy table and
  `.plot()` for an [Observable Plot](https://observablehq.com/plot/) figure through
  [pyobsplot](https://juba.github.io/pyobsplot/) (the `plot` extra).
- **In the report too.** `verify(...)` is a pydantic-evals report evaluator:
  `Dataset(..., report_evaluators=[verify("floods", contingency)])`.

## Three things to remember

1. **Pool ratios, don't average them.** POD, FAR, CSI, skill scores and FSS are computed over all
   questions together. `scores` does that by default; `preserve_dims=["question"]` gives a score
   per question when you want one, as `.paired_bootstrap(...)` needs.
2. **Always a reference.** A score only means something next to another: a simple guess, the same
   language model without tools, or the previous version of the agent.
3. **Ask for a number.** "Likely" is anywhere from 57% to 91% to the people who read it, and
   "possible" from 22% to 70%: see [how people read probability words](docs/probability-phrases.md).
   `PHRASES` holds those readings, so an agent's words can still be scored, per reader.

## Development

```bash
uv sync
uv run pytest
```

## Licence

GPL-3.0, [HKV lijn in water](https://www.hkv.nl).
