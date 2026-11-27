"""Water terms that laypeople read differently from hydrologists, from Venhuizen et al. (2019), HESS 23, 393-403.

119 laypeople in Manchester and 34 hydrologists picked one of four definitions for 12 water terms.
`WATER_TERMS` keeps, per term, the definition most hydrologists chose and the share of each group
that chose it. `Jargon` flags the terms in an answer that most laypeople read differently.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import NamedTuple

from pydantic_evals.evaluators import EvaluationReason, Evaluator, EvaluatorContext


class Term(NamedTuple):
    term: str
    meaning: str
    """The definition most hydrologists chose."""
    experts: int
    """Percent of hydrologists that chose it."""
    laypeople: int
    """Percent of laypeople that chose it."""


WATER_TERMS: dict[str, Term] = {
    t.term: t
    for t in (
        Term("river basin", "area having a common outlet for its surface runoff", 94, 13),
        Term("river", "large stream which serves as the natural drainage for a basin", 88, 15),
        Term("stream", "general term for any body of flowing water", 47, 18),
        Term("delta", "feature resulting from an alluvial deposit at a river mouth", 61, 25),
        Term("groundwater", "subsurface water occupying the saturated zone", 79, 36),
        Term("discharge", "volume of water flowing through a river cross section per unit time", 100, 45),
        Term("aquifer", "geological formation capable of storing, transmitting and yielding water", 76, 47),
        Term("dam", "barrier constructed across a valley to store water or raise the water level", 62, 47),
        Term("lake", "inland body of standing surface water of significant extent", 85, 53),
        Term("water table", "top surface of the zone of saturation", 82, 56),
        Term("downstream", "direction in which a fluid is moving", 97, 58),
        Term("flood", "overflow of water onto lands that are not normally covered by water", 76, 88),
    )
}


def water_terms(text: str) -> list[tuple[int, int, Term]]:
    """The water terms in a text as (start, end, term), in reading order.

    Terms count in lower case only, so names such as "Delta Programme" are left alone, and the longest
    term wins: "river basin" is not also "river".
    """
    found: list[tuple[int, int, Term]] = []
    for t in sorted(WATER_TERMS.values(), key=lambda t: -len(t.term)):
        for m in re.finditer(rf"\b{t.term}s?\b", text):
            if not any(a < m.end() and m.start() < b for a, b, _ in found):
                found.append((m.start(), m.end(), t))
    return sorted(found)


@dataclass
class Jargon(Evaluator):
    """Passes unless the answer uses a water term that fewer than `below` percent of laypeople read as hydrologists do."""

    below: int = 50

    def evaluate(self, ctx: EvaluatorContext) -> EvaluationReason:
        misread = dict.fromkeys(t for _, _, t in water_terms(str(ctx.output)) if t.laypeople < self.below)
        reason = "; ".join(f'"{t.term}": only {t.laypeople}% of laypeople take it as {t.meaning}' for t in misread)
        return EvaluationReason(value=not misread, reason=reason or None)
