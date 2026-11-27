# Likely, in words

An agent that says "likely" instead of a number. `PHRASES` turns each word into how cautious, average and bold readers take it ([Probability words](../probability-phrases.md)), and the Brier score shows what the same answers are worth to each of them.

=== "Code"

    ```python
    --8<-- "examples/verbal_forecast.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("verbal_forecast", "brier"))
    ```
