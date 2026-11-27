"""Run an example and show its results: the Output tab and the figure of its page."""

import json
import runpy

from pydantic_evals.reporting import EvaluationReport

from delta_agent_evals import Verification
from delta_agent_evals.plot import figure_spec


def results(name: str, *variables: str) -> str:
    found = runpy.run_path(f"examples/{name}.py")
    return "\n\n".join(text(found[v]) for v in variables)


def text(value) -> str:
    if isinstance(value, Verification):
        return value.to_frame().to_string()
    if isinstance(value, EvaluationReport):
        return value.render(include_input=True, include_output=True, include_durations=False, include_reasons=True)
    if isinstance(value, dict):
        return "\n\n".join(map(text, value.values()))
    return str(value)


def figure(name: str, variable: str) -> str:
    """The figure of `.plot()`, drawn in the browser by Observable Plot, so that its tips work."""
    df, marks, spec = figure_spec(runpy.run_path(f"examples/{name}.py")[variable])
    payload = json.dumps({"data": df.to_dict("records"), "marks": marks, "spec": spec})
    return f"""<div id="figure-{name}"></div>
<script type="module">
import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/+esm";
const {{data, marks, spec}} = {payload};
const el = document.getElementById("figure-{name}");
const plot = Plot.plot({{...spec, width: el.clientWidth, marks: marks.map(([n, d, o]) => Plot[n](d ?? data, o))}});
el.append(plot);
</script>"""
