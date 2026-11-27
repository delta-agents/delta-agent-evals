# delta-agent-evals

[![tests](https://github.com/delta-agents/delta-agent-evals/actions/workflows/tests.yaml/badge.svg)](https://github.com/delta-agents/delta-agent-evals/actions/workflows/tests.yaml)
[![docs](https://github.com/delta-agents/delta-agent-evals/actions/workflows/docs.yaml/badge.svg)](https://delta-agents.github.io/delta-agent-evals/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue)](LICENSE)

**delta-agent-evals** brings water and weather science verification to artificial intelligence (AI)
agents. Treat an agent's answer as the forecast, the reference as the observation, and compare them
with any [scores](https://github.com/nci/scores) metric on a question dataset run in
[pydantic-evals](https://ai.pydantic.dev/evals/). A single function, `verify`, handles numbers, yes
or no, probabilities, ensembles, and maps per lead time.

*Developed by [HKV lijn in water](https://www.hkv.nl) for [Delta Agents](https://delta-agents.nl).*

## Documentation

Explore the [documentation site](https://delta-agents.github.io/delta-agent-evals/): a page per
measure category, each with an interactive figure showing how the score is built. Language models
can read it via [llms.txt](https://delta-agents.github.io/delta-agent-evals/llms.txt) and
[llms-full.txt](https://delta-agents.github.io/delta-agent-evals/llms-full.txt).

## Example

Consider four questions on water depth after a dike breach and an agent that answers three. Here we
compute mean absolute error, root mean squared error, and the share within a tolerance:

```python
from pydantic_evals import Case, Dataset
from scores.continuous import mae, percent_within_x, rmse

from delta_agent_evals import each, verify

# the questions as text, with the reference answer: the water depth in metres
depths = {"fire station": 1.0, "town hall": 2.0, "school": 0.0, "pumping station": 4.0}
dataset = Dataset(
    name="depth",
    cases=[
        Case(inputs=f"If dike ring 52 breaches, how deep is the water at the {p}?", expected_output=d)
        for p, d in depths.items()
    ],
)


# the agent: here one with known answers, and none for the pumping station
async def agent(question: str) -> float | None:
    answers = {"fire station": 1.05, "town hall": 1.8, "school": 0.0}
    return next((d for p, d in answers.items() if p in question), None)


report = dataset.evaluate_sync(agent, progress=False)
errors = verify(None, mae, rmse).on(report)  # mae 0.083, rmse 0.119; the missing answer is left out
hits = verify(None, percent_within_x, threshold=each(0.1, 0.25, 0.5)).on(report)  # 67%, 100%, 100%
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/errors-dark.svg">
  <img alt="Per question the reference depth, the agent's answer and the error between them, with the band of a tolerance of 0.25 m" src="images/errors-light.svg">
</picture>

Answers can carry their own dimensions. Pass a map per lead time as a `Grid` to get the Fractions
Skill Score from `scores` at each lead time, its useful threshold, and skillful lead time. Widening
the window lets a slightly offset map remain useful for longer:

```python
from delta_agent_evals import each, fss, verify

# maps: questions answered with a map per hour, as in examples/spatial_fss.py
skill = verify(None, fss, event_threshold=0.5, window_size=each(1, 3)).on(maps)
skill["skillful_lead_time"]  # 120 min per 25 m pixel, 180 min over 75 m
```

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/maps-dark.svg">
  <img alt="The reference and the answer map every hour, a window over both, and the Fractions Skill Score against its useful level" src="images/maps-light.svg">
</picture>

## Features

- Apply any metric from `scores` to a pydantic-evals report through one entry point: `verify`.
- Evaluate scalars (numbers, yes or no, probabilities) and multidimensional types: `Grid`,
  `Ensemble`, `Series`, or anything with `to_xarray()`.
- Pool ratios over all questions rather than averaging per question; omit missing answers and count
  them per agent.
- Use repeated runs as an ensemble; sweep options with `each(...)`.
- Compare agents side by side using a reference skill score and paired bootstrap.
- Check reader interpretation: probability words like "likely" per reader (`PHRASES`) and water
  terms most laypeople misread (`Jargon`), also on live traffic.
- Get one `Verification`: an xarray Dataset, tidy table, and [Observable
  Plot](https://observablehq.com/plot/) figure; `verify(...)` is also a pydantic-evals report
  evaluator.

| Measure | Example | Use case |
|---|---|---|
| [Continuous errors](https://delta-agents.github.io/delta-agent-evals/example/continuous-errors/) | [continuous_errors.py](examples/continuous_errors.py) | How deep will the water be? |
| [Yes or no](https://delta-agents.github.io/delta-agent-evals/example/yes-or-no/) | [yes_or_no.py](examples/yes_or_no.py) | Will it flood? |
| [Maps](https://delta-agents.github.io/delta-agent-evals/example/maps/) | [spatial_fss.py](examples/spatial_fss.py) | Where is the water, every hour? |
| [Ensembles](https://delta-agents.github.io/delta-agent-evals/example/ensembles/) | [ensembles.py](examples/ensembles.py) | What will the water level be? |
| [Skill and significance](https://delta-agents.github.io/delta-agent-evals/example/skill-and-significance/) | [skill_and_significance.py](examples/skill_and_significance.py) | Better than without tools? |
| [Probability words](https://delta-agents.github.io/delta-agent-evals/example/probability-words/) | [probability_words.py](examples/probability_words.py) | How likely is it to flood? |
| [Plain language](https://delta-agents.github.io/delta-agent-evals/example/plain-language/) | [plain_language.py](examples/plain_language.py) | Do people understand the answer? |

## Installation

```bash
pip install git+https://github.com/delta-agents/delta-agent-evals
```

Or with [uv](https://docs.astral.sh/uv/) and the `plot` extra for figures:

```bash
uv add "delta-agent-evals[plot] @ git+https://github.com/delta-agents/delta-agent-evals"
```

## Getting help

Questions, bugs, or ideas? Open a [GitHub
issue](https://github.com/delta-agents/delta-agent-evals/issues).

## Development

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Read [Contributing](https://delta-agents.github.io/delta-agent-evals/contributing/) and
[CLAUDE.md](CLAUDE.md) for commands and conventions.

## Built on

delta-agent-evals relies on [scores](https://github.com/nci/scores) (Leeuwenburg et al. 2024,
<https://doi.org/10.21105/joss.06889>) for all metrics and
[pydantic-evals](https://ai.pydantic.dev/evals/) to run questions. Reader-interpretation checks draw
on Willems, Albers & Smeets (2020, <https://doi.org/10.22323/2.19020203>) and Venhuizen et al.
(2019, <https://doi.org/10.5194/hess-23-393-2019>); the useful threshold for the Fractions Skill
Score follows Roberts & Lean (2008, <https://doi.org/10.1175/2007MWR2123.1>).

## Licence

GNU General Public License (GPL) 3.0, [HKV lijn in water](https://www.hkv.nl). The
[docs/probability-phrases.md](docs/probability-phrases.md) figure is Creative Commons
Attribution-NonCommercial-NoDerivatives (CC BY-NC-ND) 4.0 by its authors.
