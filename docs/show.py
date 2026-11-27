"""Run an example and show it on its page: its results as text, and the data of its figure for docs/js/figures.js."""

import inspect
import json
import math
import re
import runpy

import numpy as np
import xarray as xr
from pydantic_evals.reporting import EvaluationReport
from scores.probability import crps_for_ensemble

from delta_agent_evals import PHRASES, Verification, answers, water_terms
from delta_agent_evals.plot import figure_spec


def run(name: str) -> dict:
    return runpy.run_path(f"examples/{name}.py")


def results(name: str, *variables: str) -> str:
    found = run(name)
    return "\n\n".join(text(found[v]) for v in variables)


def text(value) -> str:
    if isinstance(value, Verification):
        return value.to_frame().to_string()
    if isinstance(value, EvaluationReport):
        table = value.render(include_input=True, include_output=True, include_durations=False, include_reasons=True, width=100)
        return re.sub(r"\x1b\[[0-9;]*m", "", table)  # without the colours of the terminal
    if isinstance(value, dict):
        return "\n\n".join(map(text, value.values()))
    if isinstance(value, xr.Dataset):
        return value.to_pandas().to_string()
    return str(value)


def plain(value):
    """Numbers, lists and arrays as JSON, NaN as null."""
    if isinstance(value, np.ndarray | list | tuple):
        return [plain(v) for v in value]
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, np.generic):
        value = value.item()
    return None if isinstance(value, float) and math.isnan(value) else value


def figure(kind: str) -> str:
    """A figure of docs/js/figures.js, with its data from the example."""
    data = json.dumps(plain(FIGURES[kind]())).replace("</", "<\\/")
    return f'<figure class="fig" data-kind="{kind}"><script type="application/json">{data}</script></figure>'


def plot(name: str, variable: str) -> str:
    """The figure of `.plot()`, drawn in the browser by Observable Plot, so that its tips work."""
    df, marks, spec = figure_spec(run(name)[variable])
    payload = json.dumps({"data": df.to_dict("records"), "marks": marks, "spec": spec})
    return f"""<div id="plot-{name}"></div>
<script type="module">
import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/+esm";
const {{data, marks, spec}} = {payload};
const el = document.getElementById("plot-{name}");
el.append(Plot.plot({{...spec, width: el.clientWidth, marks: marks.map(([n, d, o]) => Plot[n](d ?? data, o))}}));
</script>"""


def numbers() -> dict:
    m = run("continuous_errors")
    fcst, obs, missing = answers(m["report"], None)
    hits = m["hits"]["percent_within_x"]
    return {
        "places": list(m["TRUTH"]),
        "reference": obs.values,
        "answer": fcst.isel(run=0).values,
        "mae": float(m["errors"]["mae"]),
        "rmse": float(m["errors"]["rmse"]),
        "missing": int(m["errors"].missing),
        "thresholds": hits["threshold"].values,
        "within": hits.values,
    }


def yes_or_no() -> dict:
    m = run("yes_or_no")
    said, floods, _ = answers(m["report"], "floods")
    p, _, _ = answers(m["report"], "p_floods", reference="floods")
    return {
        "places": list(m["TRUTH"]),
        "answer": said.isel(run=0).values,
        "observed": floods.values,
        "p": p.isel(run=0).values,
        "measures": {k: float(v) for k, v in m["table"].data.items()},
        "brier": float(m["brier"]["brier_score"]),
    }


def maps() -> dict:
    m = run("spatial_fss")
    fcst, obs, _ = answers(m["report"], None)
    v = m["maps"]
    return {
        "lead_time": obs["lead_time"].values,
        "reference": obs.isel(question=0).values,
        "answer": fcst.isel(question=0, run=0).values,
        "windows": v["window_size"].values,
        "fss": v["fss"].transpose("window_size", "lead_time").values,
        "useful": v["fss_useful"].isel(window_size=0).values,
        "skillful": v["skillful_lead_time"].values,
    }


def ensembles() -> dict:
    m = run("ensembles")
    fcst, obs, _ = answers(m["report"], None)
    members, observed = fcst.isel(run=0, lead_time=0), obs.isel(lead_time=0)
    crps = crps_for_ensemble(members, observed, "member", method="fair", preserve_dims=["question"])
    return {
        "times": m["TIMES"],
        "members": members.values,
        "observed": observed.values,
        "alarm": m["ALARM"],
        "crps": crps.values,
        "rank": (members < observed).sum("member").values + 1,
        "crps_mean": float(m["crps"]["crps_for_ensemble"]),
        "brier": float(m["brier"]["brier_score_for_ensemble"].squeeze()),
        "ranks": m["ranks"]["rank_histogram"].values,
    }


def skill() -> dict:
    m = run("skill_and_significance")
    per_question = m["per_question"]["mae"]
    return {
        "places": list(m["TRUTH"]),
        "agent": per_question.sel(agent="agent").values,
        "reference": per_question.sel(agent="without_tools").values,
        "mae": m["errors"]["mae"].values,
        "skill": float(m["skill"]["mae"].sel(agent="agent")),
        "bootstrap": {k: float(v) for k, v in m["bootstrap"].data_vars.items()},
        "n_boot": inspect.signature(Verification.paired_bootstrap).parameters["n_boot"].default,
    }


def words() -> dict:
    m = run("probability_words")
    readings = {w: PHRASES[w].to_xarray().values if w in PHRASES else None for w in m["WORDS"].values()}
    return {
        "places": list(m["TRUTH"]),
        "words": list(m["WORDS"].values()),
        "readings": [readings[w] for w in m["WORDS"].values()],
        "observed": list(m["TRUTH"].values()),
        "brier": m["brier"]["brier_score"].values,
    }


def marked(chunk: str) -> list:
    """The text with its water terms marked: plain strings, and {"text", "term"} for each term."""
    parts, start = [], 0
    for a, b, t in water_terms(chunk):
        parts += [chunk[start:a], {"text": chunk[a:b], "term": t.term}]
        start = b
    return [*parts, chunk[start:]]


def jargon() -> dict:
    m = run("plain_language")
    chunks = [chunk for pair in m["ANSWERS"].values() for chunk in pair]
    passed = [[c.assertions["Jargon"].value for c in r.cases] for r in m["reports"].values()]
    return {
        "questions": list(m["ANSWERS"]),
        "agents": list(m["reports"]),
        "answers": [[marked(chunk) for chunk in pair] for pair in m["ANSWERS"].values()],
        "passed": [list(p) for p in zip(*passed)],
        "terms": {t.term: t._asdict() for chunk in chunks for _, _, t in water_terms(chunk)},
        "below": 50,
    }


FIGURES = {
    "steps": numbers,
    "errors": numbers,
    "contingency": yes_or_no,
    "fss": maps,
    "ensemble": ensembles,
    "skill": skill,
    "words": words,
    "jargon": jargon,
}
