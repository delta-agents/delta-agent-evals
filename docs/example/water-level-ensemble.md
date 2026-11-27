# What will the level be?

An answer as an `Ensemble` of four members, against an observed `Series`. The ensemble measures of `scores` work as they are: `crps_for_ensemble`, `brier_score_for_ensemble` above the alarm level and `rank_histogram`.

=== "Code"

    ```python
    --8<-- "examples/water_level_ensemble.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("water_level_ensemble", "crps", "brier", "ranks"))
    ```
