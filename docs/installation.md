# Installation

delta-agent-evals needs Python 3.11 or newer:

```bash
pip install git+https://github.com/delta-agents/delta-agent-evals
```

In a project managed with [uv](https://docs.astral.sh/uv/):

```bash
uv add git+https://github.com/delta-agents/delta-agent-evals
```

## Dependencies

It installs [pydantic-evals](https://ai.pydantic.dev/evals/), [scores](https://github.com/nci/scores),
numpy, pandas and xarray. Figures with `.plot()` need the `plot` extra, which installs
[pyobsplot](https://juba.github.io/pyobsplot/):

```bash
pip install "delta-agent-evals[plot] @ git+https://github.com/delta-agents/delta-agent-evals"
```
