# logproc

Run a process and live log stdin and stdout.

## Description

This experimental module allows you to run an external program in the background
and to live capture and handle its standard output and standard error.

Each captured line of output is immediately forwarded to the logging system
(or whatever handler you provide) so that you can immediately see the output
if you are logging to console. Both an asynchronous and a synchronous API is provided.

## Basic Usage

In the simplest case, just run `execute(["ls", "-l"])`, which will run `ls -l`
and log its output with Python’s default logging system, using the logger id
`ls` and the level INFO for stdout, WARNING for stderr.

If you already run an asynchronous event loop, you can use the asynchronous API
by running `await aexecute(["ls", "-l"])` instead.

For more details, see the [API reference](api.md)

## Launching processes in parallel

Sometimes it is useful to launch multiple processes in parallel and capture
their output as it appears, while still limiting the number of concurrent
processes (e.g., to the number of available CPU cores). This is possible using
`map_unordered`. E.g.,

```python
async def render_graphs(folder: Path):
    commands = (["dot", "-Tsvg", "-o", fspath(file.with_suffix(".svg")), fspath(file)] 
                for file in folder.glob("*.dot"))
    async for result in map_unordered(aexecute, commands):
        # Process the result
        pass
```

calls `dot` for each `*.dot` file in the given folder, limiting the number of
concurrent jobs to the number of available CPU cores.
