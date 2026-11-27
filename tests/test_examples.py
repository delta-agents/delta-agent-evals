"""The examples are the documentation: their numbers, worked out by hand."""

import re
from pathlib import Path

import continuous_errors
import ensembles
import plain_language
import probability_words
import pytest
import skill_and_significance
import spatial_fss
import yes_or_no

from delta_agent_evals import PHRASES, WATER_TERMS

DOCS = Path(__file__).parents[1] / "docs"


def values(v, measure):
    return v[measure].values.tolist()


def test_continuous_errors():
    # errors 0.05, 0.2, 0 on three answers; the fourth question has none
    assert float(continuous_errors.errors["mae"]) == pytest.approx(0.25 / 3)
    assert float(continuous_errors.errors["rmse"]) == pytest.approx(((0.05**2 + 0.2**2) / 3) ** 0.5)
    assert continuous_errors.errors.missing == 1
    # of the three answers, 2, 3 and 3 are within 0.1, 0.25 and 0.5 m; the missing one is left out
    assert values(continuous_errors.hits, "percent_within_x") == pytest.approx([200 / 3, 100, 100])


def test_yes_or_no():
    table = yes_or_no.table.data
    assert float(table.probability_of_detection) == pytest.approx(2 / 3)  # 2 hits, 1 miss
    assert float(table.false_alarm_ratio) == pytest.approx(1 / 3)  # 1 false alarm of 3 warnings
    # P(yes) = 0.9, 0.4, 0.7, 1.0 against 1, 1, 0, 1
    assert float(yes_or_no.brier["brier_score"]) == pytest.approx((0.01 + 0.36 + 0.49 + 0) / 4)


def test_spatial_fss():
    # reference wet columns 0-1, 0-3, 0-5; the agent's 0-1, 1-4, 2-7. Wet are 2, 4 and 6 of 10 columns per
    # hour, so f0 = 0.2, 0.4, 0.6 and FSS_useful = 0.5 + f0 / 2 = 0.6, 0.7, 0.8
    useful = spatial_fss.maps["fss_useful"].sel(window_size=1).values.tolist()
    assert useful == pytest.approx([0.6, 0.7, 0.8])
    # per pixel, FSS = 1 - mismatches / (wet in answer + wet in reference), per row of the polder:
    # 1 - 0/4 = 1 >= 0.6, 1 - 2/8 = 0.75 >= 0.7, 1 - 4/12 = 0.667 < 0.8 -> useful for two hours
    fss = spatial_fss.maps["fss"]
    assert fss.sel(window_size=1).values.tolist() == pytest.approx([1, 0.75, 2 / 3])
    # over 3 x 3 pixels the fractions of wet columns in the 8 windows (centred on columns 1-8) are compared:
    # at 16:00 reference 3,3,2,1,0,0,0,0 and answer 2,3,3,2,1,0,0,0 thirds -> 1 - 4 / (23 + 27) = 0.92;
    # at 17:00 reference 3,3,3,3,2,1,0,0 and answer 1,2,3,3,3,3,2,1 thirds -> 1 - 15 / (41 + 46) = 0.828 >= 0.8
    assert fss.sel(window_size=3).values.tolist() == pytest.approx([1, 1 - 4 / 50, 1 - 15 / 87])
    # so the map is useful for two hours per 25 m pixel and for all three hours at 75 m
    assert spatial_fss.maps["skillful_lead_time"].values.tolist() == [120, 180]


def test_ensembles():
    # fair CRPS = mean|x - y| - sum_{i != j} |x_i - x_j| / (2 M (M - 1)) per question, then the mean
    assert float(ensembles.crps["crps_for_ensemble"]) == pytest.approx((1 / 6 + 0.1 + 0.8) / 3)
    # fair Brier of i of m = 4 members above 1.5 m against event y: (i/m - y)^2 - i (m - i) / (m^2 (m - 1));
    # i = 2, 1, 4 against y = 1, 0, 0: 0.25 - 4/48 = 1/6, 0.0625 - 3/48 = 0, 1 - 0 = 1
    brier = values(ensembles.brier, "brier_score_for_ensemble")
    assert brier == pytest.approx([(1 / 6 + 0 + 1) / 3])  # one per threshold

    # without an answer at 12:00 that question is left out
    async def no_answer_at_noon(question: str):
        if "12:00" in question:
            raise RuntimeError("no ensemble")
        return await ensembles.agent(question)

    report = ensembles.dataset.evaluate_sync(no_answer_at_noon, progress=False)
    brier = ensembles.above_alarm.on(report)
    assert int(brier.missing) == 1 and values(brier, "brier_score_for_ensemble") == pytest.approx([(1 / 6 + 0) / 2])
    # members below the observation: 2, 3, 0 -> ranks 3, 4, 1 of 5
    assert values(ensembles.ranks, "rank_histogram") == pytest.approx([1 / 3, 0, 1 / 3, 1 / 3, 0])


def test_skill_and_significance():
    assert values(skill_and_significance.errors, "mae") == pytest.approx([0.65 / 4, 5 / 4])
    assert float(skill_and_significance.skill["mae"].sel(agent="agent")) == pytest.approx(1 - 0.65 / 5)
    # per question the agent's error minus the guess's: 0.05 - 0.5, 0.2 - 0.5, 0 - 1.5, 0.4 - 2.5
    bootstrap = skill_and_significance.bootstrap
    assert float(bootstrap["mean_d"]) == pytest.approx((-0.45 - 0.3 - 1.5 - 2.1) / 4)
    # every difference is negative, so every bootstrap mean is: the agent is better in all of them
    assert float(bootstrap["a_better"]) == 1.0 and float(bootstrap["ci_upper"]) < 0


def test_probability_words():
    assert PHRASES["waarschijnlijk"] is PHRASES["likely"]
    # likely, possible, unlikely, very likely against floods, floods, dry, floods; Brier = mean (p - outcome)^2
    low = ((0.57 - 1) ** 2 + (0.22 - 1) ** 2 + 0.03**2 + (0.70 - 1) ** 2) / 4
    mean = ((0.75 - 1) ** 2 + (0.47 - 1) ** 2 + 0.16**2 + (0.86 - 1) ** 2) / 4
    high = ((0.91 - 1) ** 2 + (0.70 - 1) ** 2 + 0.36**2 + (0.95 - 1) ** 2) / 4
    assert values(probability_words.brier, "brier_score") == pytest.approx([low, mean, high])
    assert probability_words.brier.missing == 1  # "fifty-fifty" is not one of the 29 words


def test_phrase_table_in_the_docs_matches_phrases():
    rows = re.findall(
        r"^\| ([a-z ]+) \| ([a-z ]+) \| (\d+) \| (\d+)–(\d+) \|$",
        (DOCS / "probability-phrases.md").read_text(),
        re.MULTILINE,
    )
    assert [(d, e, int(m), int(lo), int(hi)) for d, e, m, lo, hi in rows] == list(dict.fromkeys(PHRASES.values()))


def test_plain_language():
    flagged = {
        name: [c.assertions["Jargon"].reason for c in report.cases if not c.assertions["Jargon"].value]
        for name, report in plain_language.reports.items()
    }
    # Table B1: discharge, river basin and groundwater are read as hydrologists do by 45%, 13% and 36% of laypeople;
    # "downstream" (58%) passes, and "river" inside "river basin" is not counted twice
    assert [r.split(":")[0] for r in flagged["hydrologist"]] == ['"discharge"', '"river basin"', '"groundwater"']
    assert flagged["plain"] == []


def test_water_terms_in_the_docs_match():
    text = (DOCS / "water-terms.md").read_text()
    rows = re.findall(r"^\| ([a-z ]+) \| ([^|]+) \| (\d+)% \| (\d+)% \|$", text, re.MULTILINE)
    assert [(t, m, int(e), int(lay)) for t, m, e, lay in rows] == list(WATER_TERMS.values())
