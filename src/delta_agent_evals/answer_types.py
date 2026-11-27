"""Answers with dimensions of their own: a map, an ensemble or a series per lead time.

Any answer with `to_xarray()` works in `verify`; these three are ready-made and serialise compactly.
"""

from __future__ import annotations

from typing import Annotated, Any

import numpy as np
import xarray as xr
from pydantic import BaseModel, ConfigDict, PlainSerializer


def _summary(a: np.ndarray) -> dict[str, Any]:
    """A raster in reports and Logfire as its shape, max and mean, not millions of numbers."""
    return {"shape": list(a.shape), "max": float(np.nanmax(a)), "mean": float(np.nanmean(a))}


class Grid(BaseModel):
    """Any quantity as a map per lead time (lead_time, y, x): rainfall, water depth, flow velocity, salinity."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    lead_time: list[float]
    data: Annotated[np.ndarray, PlainSerializer(_summary, return_type=dict)]

    def to_xarray(self) -> xr.DataArray:
        return xr.DataArray(self.data, dims=("lead_time", "y", "x"), coords={"lead_time": self.lead_time})

    def __repr__(self) -> str:
        return f"Grid({len(self.lead_time)} lead times, {self.data.shape[1]}x{self.data.shape[2]} px)"


class Ensemble(BaseModel):
    """Members per lead time (lead_time, member), e.g. water levels; verify with `crps_for_ensemble(..., "member")`."""

    lead_time: list[float]
    members: list[list[float]]

    def to_xarray(self) -> xr.DataArray:
        return xr.DataArray(self.members, dims=("lead_time", "member"), coords={"lead_time": self.lead_time})


class Series(BaseModel):
    """One value per lead time, e.g. the observed water level as reference for an `Ensemble`."""

    lead_time: list[float]
    values: list[float]

    def to_xarray(self) -> xr.DataArray:
        return xr.DataArray(self.values, dims=("lead_time",), coords={"lead_time": self.lead_time})
