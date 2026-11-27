# How good are an AI agent's answers?

delta-agent-evals measures the answers of an artificial intelligence (AI) agent with the statistics that water and weather science use to test their
models. An agent's answer is treated like a model result, the reference answer like the observation,
and any metric of [scores](https://github.com/nci/scores) compares the two over a dataset of
questions run with [pydantic-evals](https://ai.pydantic.dev/evals/).

- Numbers, yes or no, probabilities, ensembles and maps per lead time
- Ratios such as the probability of detection (POD), the critical success index (CSI) and the Fractions
  Skill Score (FSS) pooled over all questions, not averaged per question
- Agents side by side, against a baseline, with a skill score and a paired bootstrap
- How readers take probability words and water terms in an answer

Developed for [Delta Agents](https://delta-agents.nl) by [HKV lijn in water](https://www.hkv.nl); it
works with any agent evaluated with pydantic-evals.

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("steps"))
```

## Getting started

- [Installation](installation.md)
- [Example usage](example/index.md)

## User guide

- [How it works](how-it-works.md)
- Background: [reading probability words](probability-phrases.md) and [reading water terms](water-terms.md)
- [API reference](api.md): the application programming interface (API), from the docstrings

## Questions and contributing

- [Contributing](contributing.md)

delta-agent-evals is licensed under the GNU General Public License (GPL) 3.0; questions and issues are welcome on
[GitHub](https://github.com/delta-agents/delta-agent-evals).
