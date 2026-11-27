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

One kind of measure per example, each with a use case from flood management; the
[documentation](https://delta-agents.github.io/delta-agent-evals/example/) shows how each measure comes about:

| Measure | Example | Use case | Metrics |
|---|---|---|---|
| [Continuous errors](https://delta-agents.github.io/delta-agent-evals/example/continuous-errors/) | [continuous_errors.py](examples/continuous_errors.py) | How deep will the water be? | `mae`, `rmse`, `percent_within_x` |
| [Yes or no](https://delta-agents.github.io/delta-agent-evals/example/yes-or-no/) | [yes_or_no.py](examples/yes_or_no.py) | Will it flood? | `contingency`, `brier_score` |
| [Maps](https://delta-agents.github.io/delta-agent-evals/example/maps/) | [spatial_fss.py](examples/spatial_fss.py) | Where is the water, every hour? | `fss` and the skillful lead time |
| [Ensembles](https://delta-agents.github.io/delta-agent-evals/example/ensembles/) | [ensembles.py](examples/ensembles.py) | What will the water level be? | `crps_for_ensemble`, `brier_score_for_ensemble`, `rank_histogram` |
| [Skill and significance](https://delta-agents.github.io/delta-agent-evals/example/skill-and-significance/) | [skill_and_significance.py](examples/skill_and_significance.py) | Better than without tools? | `.skill(...)`, `.paired_bootstrap(...)` |
| [Probability words](https://delta-agents.github.io/delta-agent-evals/example/probability-words/) | [probability_words.py](examples/probability_words.py) | How likely is it to flood? | `PHRASES` and `brier_score` per reader |
| [Plain language](https://delta-agents.github.io/delta-agent-evals/example/plain-language/) | [plain_language.py](examples/plain_language.py) | Do people understand the answer? | `Jargon` |

## Licence

GPL-3.0, [HKV lijn in water](https://www.hkv.nl). The figure in
[docs/probability-phrases.md](docs/probability-phrases.md) is CC BY-NC-ND 4.0 by its authors.
