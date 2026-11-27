"""What an example prints when it runs as a script: the Output tab of its page."""

import contextlib
import io
import runpy


def output(name: str) -> str:
    with contextlib.redirect_stdout(io.StringIO()) as out:
        runpy.run_path(f"examples/{name}.py", run_name="__main__")
    return out.getvalue()
