# How deep?

A number in the answer: the water depth at four places. `mae` and `rmse` give the errors, `percent_within_x` how often the answer is within 0.1, 0.25 and 0.5 m, swept with `each(...)`. The agent gives no answer for the last place; it is left out and counted in `missing`.

=== "Code"

    ```python
    --8<-- "examples/how_deep.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/output.py"
    print(output("how_deep"))
    ```
