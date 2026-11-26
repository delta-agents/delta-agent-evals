"""The examples are the documentation: their numbers, worked out by hand."""

import re
from pathlib import Path

import better_than_without_tools
import dike_breach_map
import how_deep
import plain_words
import pytest
import verbal_forecast
import water_level_ensemble
import will_it_flood

from delta_agent_evals import PHRASES, WATER_TERMS

DOCS = Path(__file__).parents[1] / "docs"


def values(v, measure):
    return v[measure].values.tolist()


def test_how_deep():
    # errors 0.05, 0.2, 0 on three answers; the fourth question has none
    assert float(how_deep.errors["mae"]) == pytest.approx(0.25 / 3)
    assert float(how_deep.errors["rmse"]) == pytest.approx(((0.05**2 + 0.2**2) / 3) ** 0.5)
    assert how_deep.errors.missing == 1
    # of the three answers, 2, 3 and 3 are within 0.1, 0.25 and 0.5 m; the missing one is left out
    assert values(how_deep.hits, "percent_within_x") == pytest.approx([200 / 3, 100, 100])


def test_will_it_flood():
    table = will_it_flood.table.data
    assert float(table.probability_of_detection) == pytest.approx(2 / 3)  # 2 hits, 1 miss
    assert float(table.false_alarm_ratio) == pytest.approx(1 / 3)  # 1 false alarm of 3 warnings
    # P(yes) = 0.9, 0.4, 0.7, 1.0 against 1, 1, 0, 1
    assert float(will_it_flood.brier["brier_score"]) == pytest.approx((0.01 + 0.36 + 0.49 + 0) / 4)


def test_dike_breach_map():
    # reference wet columns 0-1, 0-3, 0-5; the agent's 0-1, 1-4, 2-7. Wet are 12 of 30 pixels over the three
    # hours, so f0 = 0.4 and FSS_useful = 0.5 + 0.4 / 2 = 0.7
    assert float(dike_breach_map.maps["fss_useful"].isel(window_size=0)) == pytest.approx(0.7)
    # per pixel, FSS = 1 - mismatches / (wet in answer + wet in reference), per row of the polder:
    # 1 - 0/4 = 1, 1 - 2/8 = 0.75, 1 - 4/12 = 0.667 -> useful for two hours
    fss = dike_breach_map.maps["fss"]
    assert fss.sel(window_size=1).values.tolist() == pytest.approx([1, 0.75, 2 / 3])
    # over 3 x 3 pixels the fractions of wet columns in the 8 windows (centred on columns 1-8) are compared:
    # at 16:00 reference 3,3,2,1,0,0,0,0 and answer 2,3,3,2,1,0,0,0 thirds -> 1 - 4 / (23 + 27) = 0.92;
    # at 17:00 reference 3,3,3,3,2,1,0,0 and answer 1,2,3,3,3,3,2,1 thirds -> 1 - 15 / (41 + 46) = 0.828
    assert fss.sel(window_size=3).values.tolist() == pytest.approx([1, 1 - 4 / 50, 1 - 15 / 87])
    # so the map is useful for two hours per 25 m pixel and for all three hours at 75 m
    assert dike_breach_map.maps["skillful_lead_time"].values.tolist() == [120, 180]


def test_water_level_ensemble():
    # fair CRPS = mean|x - y| - sum_{i != j} |x_i - x_j| / (2 M (M - 1)) per question, then the mean
    assert float(water_level_ensemble.crps["crps_for_ensemble"]) == pytest.approx((1 / 6 + 0.1 + 0.8) / 3)
    # P(> 1.5 m) = 0.5, 0.25, 1 against events 1, 0, 0
    assert float(water_level_ensemble.brier["brier_above_alarm"]) == pytest.approx((0.25 + 0.0625 + 1) / 3)
    # members below the observation: 2, 3, 0 -> ranks 3, 4, 1 of 5
    assert values(water_level_ensemble.ranks, "rank_histogram") == pytest.approx([1 / 3, 0, 1 / 3, 1 / 3, 0])


def test_better_than_without_tools():
    assert values(better_than_without_tools.errors, "mae") == pytest.approx([0.65 / 4, 5 / 4])
    assert float(better_than_without_tools.skill["mae"].sel(agent="agent")) == pytest.approx(1 - 0.65 / 5)
    # per question the agent's error minus the guess's: 0.05 - 0.5, 0.2 - 0.5, 0 - 1.5, 0.4 - 2.5
    bootstrap = better_than_without_tools.bootstrap
    assert float(bootstrap["mean_d"]) == pytest.approx((-0.45 - 0.3 - 1.5 - 2.1) / 4)
    # every difference is negative, so every bootstrap mean is: the agent is better in all of them
    assert float(bootstrap["a_better"]) == 1.0 and float(bootstrap["ci_upper"]) < 0


def test_verbal_forecast():
    assert PHRASES["waarschijnlijk"] is PHRASES["likely"]
    # likely, possible, unlikely, very likely against floods, floods, dry, floods; Brier = mean (p - outcome)^2
    low = ((0.57 - 1) ** 2 + (0.22 - 1) ** 2 + 0.03**2 + (0.70 - 1) ** 2) / 4
    mean = ((0.75 - 1) ** 2 + (0.47 - 1) ** 2 + 0.16**2 + (0.86 - 1) ** 2) / 4
    high = ((0.91 - 1) ** 2 + (0.70 - 1) ** 2 + 0.36**2 + (0.95 - 1) ** 2) / 4
    assert values(verbal_forecast.brier, "brier_score") == pytest.approx([low, mean, high])
    assert verbal_forecast.brier.missing == 1  # "fifty-fifty" is not one of the 29 words


def test_phrase_table_in_the_docs_matches_phrases():
    rows = re.findall(
        r"^\| ([a-z ]+) \| ([a-z ]+) \| (\d+) \| (\d+)–(\d+) \|$",
        (DOCS / "probability-phrases.md").read_text(),
        re.MULTILINE,
    )
    assert [(d, e, int(m), int(lo), int(hi)) for d, e, m, lo, hi in rows] == list(dict.fromkeys(PHRASES.values()))


def test_plain_words():
    flagged = {
        name: [c.assertions["Jargon"].reason for c in report.cases if not c.assertions["Jargon"].value]
        for name, report in plain_words.reports.items()
    }
    # Table B1: discharge, river basin and groundwater are read as hydrologists do by 45%, 13% and 36% of laypeople;
    # "downstream" (58%) passes, and "river" inside "river basin" is not counted twice
    assert [r.split(":")[0] for r in flagged["hydrologist"]] == ['"discharge"', '"river basin"', '"groundwater"']
    assert flagged["plain"] == []


def test_water_terms_in_the_docs_match():
    text = (DOCS / "water-terms.md").read_text()
    rows = re.findall(r"^\| ([a-z ]+) \| ([^|]+) \| (\d+)% \| (\d+)% \|$", text, re.MULTILINE)
    assert [(t, m, int(e), int(lay)) for t, m, e, lay in rows] == list(WATER_TERMS.values())
