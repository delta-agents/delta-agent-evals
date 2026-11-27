"""Measures that `scores` does not offer as one `metric(fcst, obs)`, in the same calling convention.

Each one goes straight into `verify(...)`, like any `scores` metric.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import scores.categorical
import scores.spatial
import xarray as xr

CONTINGENCY = ("probability_of_detection", "false_alarm_ratio", "critical_success_index", "frequency_bias")


def contingency(
    fcst: xr.DataArray, obs: xr.DataArray, *, measures: Iterable[str] = CONTINGENCY, **kwargs: Any
) -> xr.Dataset:
    """Yes/no answers: any measures of scores' `BinaryContingencyManager`, from one table over all questions and runs."""
    table = scores.categorical.BinaryContingencyManager(fcst, obs.broadcast_like(fcst)).transform(**kwargs)
    return xr.Dataset({m: getattr(table, m)() for m in measures})


def fss(
    fcst: xr.DataArray,
    obs: xr.DataArray,
    *,
    event_threshold: float,
    window_size: int,
    spatial_dims: tuple[str, str] = ("y", "x"),
    lead_dim: str = "lead_time",
) -> xr.Dataset:
    """Fractions Skill Score per lead time over all questions, its 'useful' level and the skillful lead time.

    Event = value >= threshold in a square window; FSS_useful = 0.5 + f0/2 with f0 the observed event
    fraction per lead time (Roberts & Lean 2008). Skillful up to the first lead time below it; NaN without answers.
    """
    obs = obs.broadcast_like(fcst)
    events = (obs >= event_threshold).where(obs.notnull() & fcst.notnull())
    useful = 0.5 + events.mean([d for d in events.dims if d != lead_dim]) / 2
    score = (
        scores.spatial.fss_2d(
            fcst,
            obs,
            event_threshold=event_threshold,
            window_size=(window_size, window_size),
            spatial_dims=spatial_dims,
            preserve_dims=[lead_dim],
            threshold_operator=np.greater_equal,
        )
        .sortby(lead_dim)
        .where(useful.notnull())  # fss_2d gives 0 where there is no answer
    )
    ok = (score >= useful).cumprod(lead_dim).astype(bool)  # True up to the first lead time that fails
    skillful = score[lead_dim].where(ok).max().fillna(0).where(score.notnull().any())
    return xr.Dataset({"fss": score, "fss_useful": useful, "skillful_lead_time": skillful})
