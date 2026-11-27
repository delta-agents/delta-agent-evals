# In plain words?

The same answers by a hydrologist and in plain words. `Jargon` flags water terms that most laypeople read differently ([Water terms](../water-terms.md)). It is an `Evaluator` per answer that needs no reference answer, so it also runs on live traffic.

=== "Code"

    ```python
    --8<-- "examples/plain_words.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/output.py"
    print(output("plain_words"))
    ```
