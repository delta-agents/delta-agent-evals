# Example usage

A dataset of questions as text, an agent, and one line of `verify`:

```python
from scores.continuous import mae, rmse

from delta_agent_evals import verify

report = dataset.evaluate_sync(agent)        # pydantic-evals: the questions as text, and an agent
errors = verify(None, mae, rmse).on(report)  # any metric of scores on the answers
errors.to_frame()
```

Each of the following pages is one file in [`examples/`](https://github.com/delta-agents/delta-agent-evals/tree/main/examples),
with its output as the site was built:

| Page | Answer | Measures |
|---|---|---|
| [How deep?](how-deep.md) | A number | `mae`, `rmse`, `percent_within_x` |
| [Will it flood?](will-it-flood.md) | Yes or no, and a probability | `contingency`, `brier_score` |
| [Where is the water?](dike-breach-map.md) | A map per hour | `fss` and the skillful lead time |
| [What will the level be?](water-level-ensemble.md) | An ensemble | `crps_for_ensemble`, `brier_score_for_ensemble`, `rank_histogram` |
| [Better than without tools?](better-than-without-tools.md) | Two agents | `.skill(...)`, `.paired_bootstrap(...)` |
| [Likely, in words](verbal-forecast.md) | A probability word | `PHRASES` and `brier_score` per reader |
| [In plain words?](plain-words.md) | Text | `Jargon` |
