"""A `Verification` as an Observable Plot figure, through pyobsplot (`pip install delta-agent-evals[plot]`)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

    from .verify import Verification

Mark = tuple[str, list | None, dict[str, Any]]
"""An Observable Plot mark as plain data: (name, data or None for the table, options), for pyobsplot or the browser."""


def plot(
    v: Verification, x: str | None = None, *, format: str | None = None, path: str | None = None, **spec: Any
) -> Any:
    """Lines over `x` (default `lead_time` when there is one) for the measures that have it, else bars.

    Of the other coordinates the last picks the colour and the one before the facet rows; with several
    measures, each gets its own facet. A tip shows the values under the pointer. `spec` goes into the
    figure, such as `title`; `format="html", path="fss.html"` writes a file outside a notebook.
    """
    from pyobsplot import Plot

    df, marks, figure = figure_spec(v, x, **spec)
    marks = [getattr(Plot, name)(df if data is None else data, options) for name, data, options in marks]
    return Plot.plot({**figure, "marks": marks}, format=format, path=path)


def figure_spec(v: Verification, x: str | None = None, **spec: Any) -> tuple[pd.DataFrame, list[Mark], dict[str, Any]]:
    """The table, the marks and the other options of the figure of `plot`, as plain data."""
    x = x if x is not None else ("lead_time" if "lead_time" in v.data.dims else None)
    data = v.data[[m for m in v.data if x is None or x in v.data[m].dims]]
    df = type(v)(data, v.missing).to_frame()
    rest = [c for c in df.columns if c not in (x, "measure", "value")]
    for col in rest:
        df[col] = df[col].astype(str)  # categories, also for numbers such as window sizes
    color = {"legend": bool(rest), **({"domain": list(dict.fromkeys(df[rest[-1]]))} if rest else {})}
    color |= spec.pop("color", {})
    many = df.measure.nunique() > 1
    if x is None:
        bars = {"x": "value", "y": rest[-1] if rest else "measure", "tip": True}
        bars |= {"fill": rest[-1], **({"fy": "measure"} if many else {})} if rest else {}
        marks: list[Mark] = [("barX", None, bars), ("ruleX", [0], {})]
        return df, marks, {"marginLeft": 180, "color": color, **spec}
    facet = {"fy": rest[-2]} if len(rest) > 1 else {"fy": "measure"} if many else {}
    line = {"x": x, "y": "value", **({"stroke": rest[-1]} if rest else {}), **facet}
    marks = [("lineY", None, line), ("dot", None, {**line, "fill": line.get("stroke", "currentColor"), "tip": True})]
    figure = {"grid": True, "color": color, "y": {"label": str(next(iter(data)))}}
    if facet:  # room for the facet labels on the right, about 7 pixels a character
        figure["marginRight"] = 20 + 7 * max(map(len, df[facet["fy"]].astype(str)))
    return df, marks, {**figure, **spec}
