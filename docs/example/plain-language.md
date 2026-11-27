# Plain language

For the wording of an answer: `Jargon` flags water terms that most laypeople read differently ([Reading water terms](../water-terms.md)). It is a pydantic-evals `Evaluator` per answer that needs no reference answer, so it also runs on live traffic.

**Use case:** the same three answers by a hydrologist and in plain words.

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("jargon"))
```

=== "Code"

    ```python
    --8<-- "examples/plain_language.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("plain_language", "reports"))
    ```
