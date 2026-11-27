# Yes or no

For an answer that is yes or no: `contingency` puts every answer in one table and gives POD, FAR, CSI and frequency bias from it. A probability in the answer gets the `brier_score` of `scores`, against the yes or no of the reference (`reference="floods"`).

**Use case:** will four places in Zutphen flood if dike ring 52 breaches? The agent has a hit, a miss, a false alarm and another hit, and says how sure it is.

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("contingency"))
```

=== "Code"

    ```python
    --8<-- "examples/yes_or_no.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("yes_or_no", "table", "brier"))
    ```
