"""delta-agent-evals: test Delta Agents with pydantic-evals and the verification measures of `scores`.

Every case is a question as text; the agent's answer is the forecast, the reference answer the
observation. `verify` runs any `scores` metric on one field of the answers, pooled over all
questions, and returns one `Verification` to read, compare or plot.
"""

from .answer_types import Ensemble, Grid, Series
from .jargon import WATER_TERMS, Jargon, Term
from .measures import contingency, fss
from .phrases import PHRASES, Phrase
from .verify import Verification, Verify, answers, each, verify

__all__ = [
    "PHRASES",
    "WATER_TERMS",
    "Ensemble",
    "Grid",
    "Jargon",
    "Phrase",
    "Series",
    "Term",
    "Verification",
    "Verify",
    "answers",
    "contingency",
    "each",
    "fss",
    "verify",
]

__version__ = "0.3.0"
