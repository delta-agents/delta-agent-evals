# How it works

pydantic-evals runs the questions; `verify` turns the answers into arrays; a metric of `scores` does
the rest.

```python
verify(field, *metrics, reference=None, **options).on(report)
```

## From answers to arrays

`field` picks what is verified in each answer and each reference answer:

- `None`: the answer itself, such as a number or a `Grid`
- `"max_depth_m"` or `"answer.max_depth_m"`: an attribute or key; a typo raises
- `lambda a: CLASSES.index(a.impact)`: any function of the answer, here an ordered class

`reference="floods"` picks another field in the reference answer, such as a probability against a
yes or no. A yes or no counts as 1 or 0. Anything with `to_xarray()` brings its own dimensions:

| Answer type | Dimensions | For |
|---|---|---|
| `Grid(lead_time, data)` | `lead_time, y, x` | A map per lead time; in a report it shows as shape, max and mean |
| `Ensemble(lead_time, members)` | `lead_time, member` | An ensemble per lead time |
| `Series(lead_time, values)` | `lead_time` | A value per lead time, such as an observed water level |

The answers become an array with a `question` and a `run` dimension. Repeated runs
(`evaluate(repeat=5)`) are the `run` dimension: an ensemble for `scores`. A missing or failed answer
is NaN (not a number), which `scores` leaves out; `.missing` counts these runs per agent.

## Metrics

A metric is any function `metric(fcst, obs, **options)`, as every metric in `scores` is. Options go
to every metric; an option given as `each(...)` is swept and becomes a coordinate:

```python
verify(None, percent_within_x, threshold=each(0.1, 0.25, 0.5))
```

Where `scores` has no single metric, delta-agent-evals adds one in the same form:

- `contingency`: the probability of detection (POD), false alarm ratio (FAR), critical success index (CSI)
  and frequency bias from one table over all questions and runs
- `fss`: the Fractions Skill Score (FSS) per lead time, its useful level 0.5 + f0/2 with f0 the observed
  fraction of events, and the skillful lead time

## The result

`.on(report)` returns a `Verification`: its `.data` is an xarray Dataset with a variable per measure,
`v["mae"]` one of them, `.to_frame()` a tidy table and `.plot()` an
[Observable Plot](https://observablehq.com/plot/) figure. Several reports go side by side along an
`agent` dimension:

```python
errors = verify(None, mae).on(agent=report, without_tools=baseline)
errors.skill("without_tools")  # 1 - error / error without tools
```

`.skill(...)` is for errors, where 0 is perfect. `.paired_bootstrap(a, b)` needs a score per
question (`preserve_dims=["question"]`) and holds for scores that add up over questions, such as the mean absolute error (MAE),
Brier and the continuous ranked probability score (CRPS), not for ratios or the root mean
squared error (RMSE).

`verify(...)` is also a report evaluator of pydantic-evals:
`Dataset(..., report_evaluators=[verify("floods", contingency)])`. `Jargon` checks one answer at a
time and needs no reference answer: `Dataset(..., evaluators=[Jargon()])`, offline or on live traffic.

## Four things to keep in mind

1. **Pool ratios, don't average them.** POD, FAR, CSI, skill scores and FSS are computed over all
   questions together, as `scores` does by default.
2. **Always a reference.** A score means something next to another: a simple guess, the same
   language model without tools, or the previous version of the agent.
3. **Ask for a number.** "Likely" is anywhere from 57% to 91% to the people who read it:
   see [probability words](probability-phrases.md).
4. **Mind the jargon.** Only 13% of laypeople read "river basin" as a hydrologist does:
   see [water terms](water-terms.md).
