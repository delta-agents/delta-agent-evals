# Ensembles

For an answer that is an `Ensemble`: the ensemble measures of `scores` as they are, here the fair continuous ranked probability score (CRPS) with `crps_for_ensemble`, `brier_score_for_ensemble` above a threshold and `rank_histogram`.

**Use case:** what will the water level at the Zutphen gauge be in 6 hours? The agent answers with four members, three times.

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("ensemble"))
```

=== "Code"

    ```python
    --8<-- "examples/ensembles.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("ensembles", "crps", "brier", "ranks"))
    ```
