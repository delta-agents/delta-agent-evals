# Probability words

For an answer in words: `PHRASES` turns each of 29 probability words into how cautious, average and bold readers take it ([Reading probability words](../probability-phrases.md)), and `brier_score` shows what the same answers are worth to each of them.

**Use case:** how likely is a place in Zutphen to flood? The agent answers "likely" instead of a number.

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("words"))
```

=== "Code"

    ```python
    --8<-- "examples/probability_words.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("probability_words", "brier"))
    ```
