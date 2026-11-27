# Where is the water?

A map per hour after a dike breach, as a `Grid`. The agent places the water one 25 m pixel too far east every hour. Per pixel its map is useful for two hours; over a window of 3 pixels (75 m), for all three. `fss` gives the Fractions Skill Score per lead time, the level at which it is useful (Roberts & Lean 2008) and the skillful lead time.

=== "Code"

    ```python
    --8<-- "examples/dike_breach_map.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/output.py"
    print(output("dike_breach_map"))
    ```

`.plot()` draws the FSS per lead time, one line per window size:

```python exec="on" html="true"
import pathlib, runpy, tempfile
maps = runpy.run_path("examples/dike_breach_map.py")["maps"]
path = pathlib.Path(tempfile.mkdtemp(), "fss.html")
maps.plot(format="html", path=str(path))
print(path.read_text())
```
