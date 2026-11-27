# Continuous errors

For an answer that is a number: `mae` and `rmse` of `scores` give the error, `percent_within_x` how often the answer is within a tolerance, swept with `each(...)`.

**Use case:** how deep will the water be at four places in Zutphen if dike ring 52 breaches? The agent does not answer for the last place.

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("errors"))
```

=== "Code"

    ```python
    --8<-- "examples/continuous_errors.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("continuous_errors", "errors", "hits"))
    ```
