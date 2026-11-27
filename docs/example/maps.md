# Maps

For an answer that is a map per lead time, a `Grid`: `fss` gives the Fractions Skill Score (FSS) per lead time, the level from which it is useful (Roberts & Lean 2008) and the skillful lead time. A wider window forgives a map that is a little off.

**Use case:** where is the water after a dike breach, every hour? The agent places the water one 25 m pixel too far east every hour.

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("fss"))
```

=== "Code"

    ```python
    --8<-- "examples/spatial_fss.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("spatial_fss", "maps"))
    ```

`.plot()` draws the same scores; the pointer shows the values:

```python exec="on" html="true"
--8<-- "docs/show.py"
print(plot("spatial_fss", "maps"))
```
