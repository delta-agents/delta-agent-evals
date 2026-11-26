"""Any `scores` metric on the answers in a pydantic-evals report.

The answers and the reference answers of a report become two xarray arrays with a `question` and
a `run` dimension (and the answer's own dimensions, such as `lead_time`, `y`, `x`). A missing or
failed answer is NaN, which `scores` leaves out. Every metric of `scores` takes `(fcst, obs, ...)`
and pools over all dimensions unless told otherwise, so ratios such as POD or FSS are pooled over
all questions, never averaged per question.
"""

from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Self

import numpy as np
import pandas as pd
import xarray as xr
from pydantic_evals.evaluators.report_evaluator import ReportEvaluator, ReportEvaluatorContext
from pydantic_evals.reporting import EvaluationReport
from pydantic_evals.reporting.analyses import ReportAnalysis, ScalarResult, TableResult

Field = str | Callable[[Any], Any] | None
"""A dotted path into the answer (`"answer.max_depth_m"`), a function of the answer, or None for the answer itself."""


def _value(answer: Any, path: Field) -> xr.DataArray:
    """The field of one answer: a number, a bool as 0/1, or anything with `to_xarray()`; NaN when there is none."""
    if answer is not None and callable(path):
        answer = path(answer)
    elif answer is not None and path is not None:
        for part in path.split("."):
            answer = answer.get(part) if isinstance(answer, dict) else getattr(answer, part, None)
    if hasattr(answer, "to_xarray"):
        return answer.to_xarray().astype(float)
    return xr.DataArray(np.nan if answer is None else float(answer))


def answers(report: EvaluationReport, path: Field, reference: Field = None) -> tuple[xr.DataArray, xr.DataArray, int]:
    """The answers as `(question, run, ...)`, the references as `(question, ...)`, and the number of runs without an answer.

    `reference` is the path into the reference answer when it differs from `path`. Repeated runs
    (`evaluate(repeat=N)`) share a question; a failed run is NaN.
    """
    runs: dict[str, list[Any]] = defaultdict(list)
    for c in [*report.cases, *report.failures]:
        runs[c.source_case_name or c.name].append(c)
    fcst, obs = [], []
    for cases in runs.values():
        ref = _value(cases[0].expected_output, path if reference is None else reference)
        out = [_value(getattr(c, "output", None), path).broadcast_like(ref) for c in cases]
        fcst.append(xr.concat(xr.broadcast(*out), dim=pd.RangeIndex(len(out), name="run")))
        obs.append(ref)
    questions = pd.Index(list(runs), name="question")
    fcst_da = xr.concat(xr.broadcast(*fcst), dim=questions, join="outer")  # a missing answer is NaN in every dimension
    missing = int(fcst_da.isnull().all([d for d in fcst_da.dims if d not in ("question", "run")]).sum())
    return fcst_da, xr.concat(obs, dim=questions), missing


class each(tuple):
    """Sweep an option: `event_threshold=each(0.1, 0.5)` computes both and adds an `event_threshold` coordinate.

    Several sweeps give every combination; the coordinates come out sorted.
    """

    def __new__(cls, *values: Any) -> Self:
        return super().__new__(cls, values)


@dataclass
class Verification:
    """The measures of one field: an xarray Dataset with a coordinate per agent, swept option or kept dimension."""

    data: xr.Dataset
    missing: int
    """Runs without an answer, left out of every measure."""

    def __getitem__(self, measure: str) -> xr.DataArray:
        return self.data[measure]

    def to_frame(self) -> pd.DataFrame:
        """A tidy table: one row per measure and coordinate."""
        return pd.concat([_frame(self.data[m], str(m)) for m in self.data], ignore_index=True)

    def skill(self, reference: str, dim: str = "agent") -> Verification:
        """1 - score / score of the reference, for errors (lower = better): 1 is perfect, 0 no better."""
        return Verification(1 - self.data / self.data.sel({dim: reference}, drop=True), self.missing)

    def paired_bootstrap(
        self, a: str, b: str, *, measure: str | None = None, n_boot: int = 10_000, seed: int = 0
    ) -> xr.Dataset:
        """Is agent `a` really better than `b`? A bootstrap over questions of d = score_a - score_b.

        Needs a score per question: `verify(..., preserve_dims=["question"]).on(a=..., b=...)`.
        `a_better` is the fraction of bootstrap means with d < 0, for errors (lower = better).
        """
        da = self.data[measure or next(iter(self.data))]
        if "question" not in da.dims:
            raise ValueError("Needs a score per question: verify(..., preserve_dims=['question'])")
        d = (da.sel(agent=a) - da.sel(agent=b)).dropna("question").values
        means = d[np.random.default_rng(seed).integers(0, len(d), (n_boot, len(d)))].mean(axis=1)
        lower, upper = np.quantile(means, [0.025, 0.975])
        stats = {"n": len(d), "mean_d": d.mean(), "ci_lower": lower, "ci_upper": upper}
        return xr.Dataset(stats | {"a_better": (means < 0).mean(), "b_better": (means > 0).mean()})

    def plot(self, x: str | None = None, **options: Any) -> Any:
        """An Observable Plot figure (needs the `plot` extra); see `delta_agent_evals.plot.plot`."""
        from .plot import plot

        return plot(self, x, **options)

    def to_analysis(self, title: str) -> ReportAnalysis:
        """A pydantic-evals analysis: one number, or the tidy table."""
        df = self.to_frame()
        note = f"{self.missing} runs without an answer left out"
        if len(df) == 1:
            return ScalarResult(title=title, value=round(float(df.value[0]), 4), description=note)
        rows = df.round(4).astype(object).where(df.notna(), None).values.tolist()
        return TableResult(title=title, description=note, columns=list(df.columns), rows=rows)


def _frame(da: xr.DataArray, name: str) -> pd.DataFrame:
    if not da.dims:
        return pd.DataFrame({"measure": [name], "value": [float(da)]})
    df = da.to_dataframe(name="value").reset_index()[[*da.dims, "value"]]
    return df.assign(measure=name)[[*da.dims, "measure", "value"]]


@dataclass(repr=False)
class Verify(ReportEvaluator):
    """`scores` metrics on one field of the answers; build it with `verify(...)`."""

    field: Field
    metrics: tuple[Callable[..., Any], ...]
    options: dict[str, Any] = field(default_factory=dict)
    reference: Field = None

    def on(self, *reports: EvaluationReport, **named: EvaluationReport) -> Verification:
        """Verify one report, or several side by side along an `agent` dimension (named, or by report name)."""
        named = {r.name: r for r in reports} | named
        results = {name: self._one(r) for name, r in named.items()}
        data = xr.concat([d for d, _ in results.values()], dim=pd.Index(list(named), name="agent"))
        return Verification(
            data if len(named) > 1 else data.squeeze("agent", drop=True), sum(m for _, m in results.values())
        )

    def _one(self, report: EvaluationReport) -> tuple[xr.Dataset, int]:
        fcst, obs, missing = answers(report, self.field, self.reference)
        swept = {k: v for k, v in self.options.items() if isinstance(v, each)}
        fixed = {k: v for k, v in self.options.items() if k not in swept}
        results = [
            xr.merge([_dataset(m(fcst, obs, **fixed, **dict(zip(swept, combo))), m) for m in self.metrics]).expand_dims(
                {k: [v] for k, v in zip(swept, combo)}
            )
            for combo in itertools.product(*swept.values())
        ]
        return (xr.combine_by_coords(results) if swept else results[0]), missing

    def evaluate(self, ctx: ReportEvaluatorContext) -> ReportAnalysis:
        return self.on(ctx.report).to_analysis(f"{_name(self.field)}: {', '.join(map(_name, self.metrics))}")


def _name(f: Any) -> str:
    return f if isinstance(f, str) else getattr(f, "__name__", "answer" if f is None else repr(f))


def _dataset(result: xr.DataArray | xr.Dataset, metric: Callable[..., Any]) -> xr.Dataset:
    return result if isinstance(result, xr.Dataset) else result.to_dataset(name=_name(metric))


def verify(field: Field, *metrics: Callable[..., Any], reference: Field = None, **options: Any) -> Verify:
    """Verify one field of the answers with any `scores` metrics.

    `verify("max_depth_m", mae, rmse).on(report)`; options go to every metric, and an option given
    as `each(...)` is swept. Use it as a report evaluator too: `report_evaluators=[verify(...)]`.
    """
    return Verify(field, metrics, options, reference)
