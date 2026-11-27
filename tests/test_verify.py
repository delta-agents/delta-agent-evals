"""verify on real Datasets of questions as text: repeated runs, failed runs, report evaluators and the result."""

import itertools
from collections import defaultdict

import numpy as np
import pytest
from pydantic import BaseModel
from pydantic_evals import Case, Dataset
from scores.continuous import mae
from scores.probability import crps_for_ensemble

from delta_agent_evals import Grid, answers, each, fss, verify

QUESTIONS = {
    f"How deep is the water at {place} if dike ring 52 breaches?": depth
    for place, depth in [("the fire station", 1.0), ("the town hall", 2.0)]
}
DATASET = Dataset(name="depth", cases=[Case(inputs=q, expected_output=d) for q, d in QUESTIONS.items()])


def test_repeated_runs_are_an_ensemble():
    counter = defaultdict(itertools.count)

    async def wobbly(question: str) -> float:  # -0.1, 0 and +0.1 around the truth on three runs
        return QUESTIONS[question] + (next(counter[question]) - 1) * 0.1

    report = DATASET.evaluate_sync(wobbly, repeat=3, progress=False, max_concurrency=1)
    fcst, obs, missing = answers(report, None)
    assert dict(fcst.sizes) == {"question": 2, "run": 3} and dict(obs.sizes) == {"question": 2} and missing == 0
    # fair CRPS of {-0.1, 0, 0.1} around the truth: mean|x - y| = 0.2/3, spread term 0.8/12
    v = verify(None, crps_for_ensemble, ensemble_member_dim="run", method="fair").on(report)
    assert float(v["crps_for_ensemble"]) == pytest.approx(0.2 / 3 - 0.8 / 12)


def test_a_failed_run_is_a_missing_answer():
    async def flaky(question: str) -> float:
        if "town hall" in question:
            raise RuntimeError("the flood model did not answer")
        return 1.5

    v = verify(None, mae).on(DATASET.evaluate_sync(flaky, progress=False))
    assert v.missing == 1 and float(v["mae"]) == pytest.approx(0.5)


def test_a_function_of_the_answer_as_field():
    class Answer(BaseModel):
        impact: str

    classes = ["none", "low", "medium", "high"]
    ds = Dataset(
        name="impact",
        cases=[
            Case(
                inputs="What is the impact on the A12 if dike ring 52 breaches?", expected_output=Answer(impact="high")
            )
        ],
    )

    async def agent(question: str) -> Answer:
        return Answer(impact="medium")

    v = verify(lambda a: classes.index(a.impact), mae).on(ds.evaluate_sync(agent, progress=False))
    assert float(v["mae"]) == 1  # one class off


def test_report_evaluator_and_tidy_table():
    async def agent(question: str) -> float:
        return QUESTIONS[question] + 0.2

    ds = Dataset(name="depth", cases=DATASET.cases, report_evaluators=[verify(None, mae, preserve_dims=["question"])])
    report = ds.evaluate_sync(agent, progress=False)
    assert not report.report_evaluator_failures
    (table,) = report.analyses
    assert table.columns == ["question", "measure", "value"] and [r[2] for r in table.rows] == [0.2, 0.2]


def test_sweeps_and_agents_become_coordinates():
    async def a(question: str) -> float:
        return QUESTIONS[question] + 0.2

    async def b(question: str) -> float:
        return 0.0

    def shifted_mae(fcst, obs, offset, **options):
        return mae(fcst + offset, obs, **options)

    runs = {"a": DATASET.evaluate_sync(a, progress=False), "b": DATASET.evaluate_sync(b, progress=False)}
    v = verify(None, shifted_mae, offset=each(0.0, -0.2)).on(**runs)
    # a is 0.2 m too deep: no error once shifted back by 0.2; the coordinates come out sorted
    assert v["shifted_mae"].sel(agent="a").values.tolist() == pytest.approx([0.0, 0.2])
    assert v["offset"].values.tolist() == [-0.2, 0.0]
    assert list(v.to_frame().columns) == ["agent", "offset", "measure", "value"]
    with pytest.raises(ValueError, match="per question"):
        verify(None, mae).on(**runs).paired_bootstrap("a", "b")
    # a swept option is one more dimension: select it before the bootstrap
    swept = verify(None, shifted_mae, offset=each(0.0, -0.2), preserve_dims=["question"]).on(**runs)
    with pytest.raises(ValueError, match="offset"):
        swept.paired_bootstrap("a", "b")


def test_fss_worked_out_by_hand():
    # a 1 x 4 polder, wet (1 m) in its west half; the map is right after 10 minutes and mirrored after 20
    wet_west = np.array([[[1.0, 1.0, 0.0, 0.0]]] * 2)
    answer = Grid(lead_time=[10, 20], data=np.array([[[1.0, 1.0, 0.0, 0.0]], [[0.0, 0.0, 1.0, 1.0]]]))
    ds = Dataset(
        name="wet",
        cases=[
            Case(
                inputs="Where is the polder wet in 10 and 20 minutes?",
                expected_output=Grid(lead_time=[10, 20], data=wet_west),
            )
        ],
    )

    async def agent(question: str) -> Grid:
        return answer

    v = verify(None, fss, event_threshold=0.5, window_size=1).on(ds.evaluate_sync(agent, progress=False))
    # per pixel FSS = 1 - sum (f - o)^2 / (sum f^2 + sum o^2): 1 - 0/4 = 1 after 10 min, 1 - 4/4 = 0 after 20
    assert v["fss"].values.tolist() == [1.0, 0.0]
    # f0 = 2 of 4 pixels wet at both lead times: useful = 0.5 + 0.5 / 2 = 0.75, met after 10 min and not after 20
    assert v["fss_useful"].values.tolist() == [0.75, 0.75] and float(v["skillful_lead_time"]) == 10

    async def silent(question: str) -> Grid:
        raise RuntimeError("the flood model did not answer")

    # without any answer there is no skillful lead time, not one of 0
    v = verify(None, fss, event_threshold=0.5, window_size=1).on(ds.evaluate_sync(silent, progress=False))
    assert v.missing == 1 and np.isnan(float(v["skillful_lead_time"]))


def test_a_typo_in_the_field_raises():
    async def agent(question: str) -> float:
        return 1.0

    with pytest.raises(AttributeError, match="max_dpeth_m"):
        verify("max_dpeth_m", mae).on(DATASET.evaluate_sync(agent, progress=False))


def test_reports_need_distinct_names():
    async def agent(question: str) -> float:
        return 1.0

    # two runs of the same task have the same report name: one would silently replace the other
    twice = [DATASET.evaluate_sync(agent, progress=False) for _ in range(2)]
    with pytest.raises(ValueError, match="distinct names"):
        verify(None, mae).on(*twice)
    assert verify(None, mae).on(first=twice[0], second=twice[1])["agent"].values.tolist() == ["first", "second"]


def test_plot_lines_per_lead_time(tmp_path):
    pytest.importorskip("pyobsplot")
    import dike_breach_map

    path = tmp_path / "fss.html"
    dike_breach_map.maps.plot(format="html", path=str(path), title="FSS of the breach map")
    svg = path.read_text()
    # one colour per window: both window sizes in the legend
    assert "FSS of the breach map" in svg and all(f">{w}<" in svg for w in (1, 3))
