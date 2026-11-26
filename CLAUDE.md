# delta-agent-evals: notes for agents and contributors

delta-agent-evals tests Delta Agents with the verification methods we already use for forecasts: an
agent's answer is the forecast, the reference answer is the observation. One function, `verify`, runs any
[scores](https://github.com/nci/scores) metric on the answers in a [pydantic-evals](https://ai.pydantic.dev/evals/)
report and returns one `Verification`.

## Commands

```bash
uv sync                               # environment and dev tools
uv run ruff check src tests examples  # lint (CI)
uv run ruff format src tests examples # format
uv run pytest -q                      # tests, including every example (CI)
uv run examples/dike_breach_map.py    # one example
```

Run the lint and the tests before every commit. Commit with a DCO sign-off (`git commit -s`).

## Working agreements

- **Language:** English in code, docstrings, report titles and labels, docs, commit messages, issues and
  pull requests.
- **Commits:** a commit message is one short line, plus the DCO `Signed-off-by` that `git commit -s` adds.
  No `Co-Authored-By`, no "Generated with/by Claude Code" footer or other additions, in pull requests,
  issues and comments either.
- **Pull requests:** short: what and why, and one line on what the change was based on. No report of local
  checks; CI runs them.
- **Titles** of issues, pull requests and their squash commits follow
  [Conventional Commits](https://www.conventionalcommits.org): `type(scope): summary`, the summary
  lowercase and imperative. Types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `ci`, `chore`.
  Scopes: `verify`, `measures`, `answers`, `plot`, `examples`, `readme`.
- **Versions** follow [semantic versioning](https://semver.org): `pyproject.toml` and `__version__` carry
  it. Before 1.0, `feat` raises the minor version and `fix` the patch.
- **Review before every commit** (hook in `.claude/settings.local.json`, local and not in git): the lint and
  the tests, then a review of the diff: a) can it be less verbose, b) can it be smarter and more compact,
  idiomatic Python (numpy and xarray over loops where that reads better), c) no build history in the code,
  d) comments and docs are functional, without references to issues, plans or people.
- **Think along critically:** look beyond the question. If a name, structure or choice no longer fits, or a
  change affects something elsewhere (score names, README, tests), raise it with a proposal.
- **No mocks in tests.** Tests run real `Dataset`s of questions as text with a small agent function whose
  answers are known, and check the measures against values worked out by hand.
- **Data:** answers, questions or reference data from clients or projects never go in git. Example data is
  fictitious.

## Layout

| Path | Role |
|---|---|
| `src/delta_agent_evals/verify.py` | `answers` (a report as `(question, run, ...)` arrays), `verify`, `each`, `Verification` (with `.skill`, `.paired_bootstrap`, `.plot`) |
| `src/delta_agent_evals/measures.py` | What `scores` lacks as one `metric(fcst, obs)`: `contingency` and `fss` with the skillful lead time |
| `src/delta_agent_evals/answer_types.py` | Answers with dimensions: `Grid`, `Ensemble`, `Series` |
| `src/delta_agent_evals/plot.py` | A `Verification` as an Observable Plot figure (optional `plot` extra) |
| `examples/` | One question type per file, runnable; `tests/test_examples.py` checks their numbers |

## Conventions

- A case's `inputs` is always the question as text, as a user would ask it; `expected_output` is the
  reference answer. Test agents are small functions from that text to a known answer.
- A measure is a function `metric(fcst, obs, **options)` returning a DataArray or Dataset, like every
  metric in `scores`. Use the `scores` metric when it exists; write a function in `measures.py` only for
  what it lacks. No evaluator class per measure.
- `scores` pools over all dimensions unless told otherwise, so ratios (POD, FAR, CSI, FSS, skill scores)
  are pooled over all questions and runs, never averaged per question.
- A missing or failed answer is NaN, which `scores` leaves out; `Verification.missing` counts them.
- Repeated runs (`evaluate(repeat=N)`) are the `run` dimension, an ensemble for `scores`.
- Every example has a test with its numbers worked out by hand in a comment.
- No new dependency without a reason in the pull request; plotting stays an optional extra.
