"""A `Verification` as an Observable Plot figure, through pyobsplot (`pip install delta-agent-evals[plot]`)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .verify import Verification


def plot(
    v: Verification, x: str | None = None, *, format: str | None = None, path: str | None = None, **spec: Any
) -> Any:
    """Lines over `x` (default `lead_time` when there is one) for the measures that have it, else bars.

    Of the other coordinates the last picks the colour and the one before the facet rows; with several
    measures, each gets its own facet. `spec` goes into the figure, such as `title`;
    `format="html", path="fss.html"` writes a file outside a notebook.
    """
    from pyobsplot import Plot

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
        bars = {"x": "value", "y": rest[-1] if rest else "measure"}
        bars |= {"fill": rest[-1], **({"fy": "measure"} if many else {})} if rest else {}
        marks = [Plot.barX(df, bars), Plot.ruleX([0])]
        return Plot.plot({"marks": marks, "marginLeft": 180, "color": color, **spec}, format=format, path=path)
    facet = {"fy": rest[-2]} if len(rest) > 1 else {"fy": "measure"} if many else {}
    line = {"x": x, "y": "value", **({"stroke": rest[-1]} if rest else {}), **facet}
    marks = [Plot.lineY(df, line), Plot.dot(df, {**line, "fill": line.get("stroke", "currentColor")})]
    figure = {"marks": marks, "grid": True, "color": color, "y": {"label": str(next(iter(data)))}, **spec}
    return Plot.plot(figure, format=format, path=path)
