# Skill and significance

For two agents side by side: `.on(agent=..., without_tools=...)` adds an `agent` dimension, `.skill("without_tools")` the skill score against the reference, and `.paired_bootstrap(...)` whether the difference holds over the questions.

**Use case:** is the agent with a flood model better than the same language model without tools, which can only guess the water depth?

```python exec="on" html="true"
--8<-- "docs/show.py"
print(figure("skill"))
```

=== "Code"

    ```python
    --8<-- "examples/skill_and_significance.py"
    ```

=== "Output"

    ```python exec="on" result="text"
    --8<-- "docs/show.py"
    print(results("skill_and_significance", "errors", "skill", "bootstrap"))
    ```
