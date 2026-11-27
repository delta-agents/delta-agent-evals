# Better than without tools?

The same questions to the agent and to the language model without tools. `.on(agent=..., without_tools=...)` puts them side by side, `.skill("without_tools")` gives 1 - error / error without tools, and `.paired_bootstrap(...)` whether the difference holds over the questions.

=== "Code"

    ```python
    --8<-- "examples/better_than_without_tools.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/output.py"
    print(output("better_than_without_tools"))
    ```
