"""Is the agent better than the same language model without tools? Skill score and a paired bootstrap."""

from pydantic_evals import Case, Dataset
from scores.continuous import mae

from delta_agent_evals import verify

TRUTH = {"fire station": 1.0, "town hall": 2.0, "school": 0.0, "pumping station": 4.0}
ANSWERS = {"fire station": 1.05, "town hall": 1.8, "school": 0.0, "pumping station": 3.6}

dataset = Dataset(
    name="how_deep",
    cases=[
        Case(inputs=f"If dike ring 52 breaches, how deep is the water at the {p} in Zutphen?", expected_output=d)
        for p, d in TRUTH.items()
    ],
)


async def agent(question: str) -> float:
    return next(d for p, d in ANSWERS.items() if p in question)


async def without_tools(question: str) -> float:
    return 1.5  # a language model without the flood model guesses


runs = {
    "agent": dataset.evaluate_sync(agent, progress=False),
    "without_tools": dataset.evaluate_sync(without_tools, progress=False),
}
errors = verify(None, mae).on(**runs)
skill = errors.skill("without_tools")
per_question = verify(None, mae, preserve_dims=["question"]).on(**runs)
bootstrap = per_question.paired_bootstrap("agent", "without_tools")

if __name__ == "__main__":
    print(errors.to_frame(), skill.to_frame(), bootstrap, sep="\n\n")
