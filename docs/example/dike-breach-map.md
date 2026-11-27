# Where is the water?

A map per hour after a dike breach, as a `Grid`. The agent places the water one 25 m pixel too far east every hour. Per pixel its map is useful for two hours; over a window of 3 pixels (75 m), for all three. `fss` gives the Fractions Skill Score per lead time, the level at which it is useful (Roberts & Lean 2008) and the skillful lead time.

=== "Code"

    ```python
    --8<-- "examples/dike_breach_map.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("dike_breach_map", "maps"))
    ```

`.plot()` draws the FSS per lead time, one line per window size; the pointer shows the values:

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("dike_breach_map", "maps"))
```
