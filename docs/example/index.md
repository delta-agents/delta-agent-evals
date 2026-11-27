# Example usage

A dataset of questions as text, an agent, and one line of `verify`:

```python
from scores.continuous import mae, rmse

from delta_agent_evals import verify

report = dataset.evaluate_sync(agent)        # pydantic-evals: the questions as text, and an agent
errors = verify(None, mae, rmse).on(report)  # any metric of scores on the answers
errors.to_frame()
```

Each of the following pages is one kind of measure, with a use case from flood management as its example:
a figure that shows how the measure comes about, the file in
[`examples/`](https://github.com/delta-agents/delta-agent-evals/tree/main/examples), and its output as the
site was built.

| Measure | Answer | Use case |
|---|---|---|
| [Continuous errors](continuous-errors.md) | A number | How deep will the water be? |
| [Yes or no](yes-or-no.md) | Yes or no, and a probability | Will it flood? |
| [Maps](maps.md) | A map per lead time | Where is the water, every hour? |
| [Ensembles](ensembles.md) | An ensemble | What will the water level be? |
| [Skill and significance](skill-and-significance.md) | Two agents | Better than without tools? |
| [Probability words](probability-words.md) | A word such as "likely" | How likely is it to flood? |
| [Plain language](plain-language.md) | Text | Do people understand the answer? |
