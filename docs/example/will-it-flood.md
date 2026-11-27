# Will it flood?

A yes or no, and the agent's confidence in it. `contingency` puts all answers in one table (hits, misses, false alarms) for POD, FAR, CSI and frequency bias; `brier_score` scores the confidence against the yes or no of the reference, with `reference="floods"`.

=== "Code"

    ```python
    --8<-- "examples/will_it_flood.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("will_it_flood", "table", "brier"))
    ```
