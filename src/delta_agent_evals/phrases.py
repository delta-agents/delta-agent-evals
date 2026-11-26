"""How people read probability words, from Willems, Albers & Smeets (2020), JCOM 19(02) A03.

881 Dutch readers put 29 Dutch words on a 0-100% scale. Each `Phrase` keeps the mean and the
5%-95% range of their answers; `PHRASES` finds it by the Dutch word or the paper's English
translation. As an answer field, a phrase is a probability per `reading`: low, mean and high.
"""

from __future__ import annotations

from typing import NamedTuple

import xarray as xr


class Phrase(NamedTuple):
    dutch: str
    english: str
    mean: int
    """Mean reading in percent."""
    low: int
    """5th percentile of the readings in percent."""
    high: int
    """95th percentile of the readings in percent."""

    def to_xarray(self) -> xr.DataArray:
        """The probability per reading: what a cautious, an average and a bold reader takes the word to mean."""
        return (
            xr.DataArray([self.low, self.mean, self.high], dims="reading", coords={"reading": ["low", "mean", "high"]})
            / 100
        )


PHRASES: dict[str, Phrase] = {
    name: p
    for p in (
        Phrase("altijd", "always", 96, 81, 100),
        Phrase("zeker", "certain", 96, 82, 100),
        Phrase("bijna zeker", "almost certain", 88, 71, 98),
        Phrase("bijna altijd", "almost always", 87, 70, 96),
        Phrase("zeer waarschijnlijk", "very likely", 86, 70, 95),
        Phrase("heel vaak", "very often", 79, 60, 95),
        Phrase("grote kans", "high chance", 78, 60, 92),
        Phrase("doorgaans", "generally", 76, 59, 94),
        Phrase("meestal", "usually", 76, 58, 91),
        Phrase("waarschijnlijk", "likely", 75, 57, 91),
        Phrase("te verwachten", "expected", 75, 52, 93),
        Phrase("vaak", "often", 73, 58, 90),
        Phrase("vermoedelijk", "probable", 67, 41, 86),
        Phrase("mogelijk", "possible", 47, 22, 70),
        Phrase("misschien", "maybe", 41, 17, 60),
        Phrase("onzeker", "uncertain", 40, 17, 59),
        Phrase("kans", "chance", 40, 11, 61),
        Phrase("kan gebeuren", "liable to happen", 38, 10, 60),
        Phrase("twijfelachtig", "doubtful", 34, 10, 54),
        Phrase("soms", "sometimes", 33, 11, 55),
        Phrase("niet vaak", "not often", 24, 9, 48),
        Phrase("kleine kans", "low chance", 17, 5, 32),
        Phrase("onwaarschijnlijk", "unlikely", 16, 3, 36),
        Phrase("zelden", "rarely", 13, 2, 30),
        Phrase("bijna nooit", "almost never", 13, 2, 35),
        Phrase("bijna onmogelijk", "almost impossible", 11, 1, 40),
        Phrase("zeer onwaarschijnlijk", "very unlikely", 11, 2, 26),
        Phrase("nooit", "never", 6, 0, 32),
        Phrase("onmogelijk", "impossible", 6, 0, 21),
    )
    for name in (p.dutch, p.english)
}
