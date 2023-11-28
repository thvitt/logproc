#!/usr/bin/env python
"""Run a process and log stdin and stdout."""

__version__ = "0.1.0"


import asyncio
from collections.abc import Callable, Sequence
import logging

OutputCallback = Callable[[str | bytes], None]
LoggerSpec = str | logging.Logger | None
OutputHandler = OutputCallback | LoggerSpec


def proc_logger(logger: LoggerSpec = None, level: int = logging.INFO) -> OutputCallback:
    """
    Creates a callback that logs to a logger.

    Args:
        logger: If given, this is either a logger or the name of a logger. If missing, we log to the root logger.
        level: The level at which to log the messages
    """
    if logger is None:
        logger = logging.getLogger()
    elif isinstance(logger, str):
        logger = logging.getLogger(logger)

    def log(line: bytes | str):
        if isinstance(line, bytes):
            line = line.decode(errors="replace").rstrip()
        logger.log(level, line)

    return log


async def _read_stream(stream, cb: OutputCallback):
    while line := await stream.readline():
        cb(line)


async def _stream_subprocess(cmd, stdout_cb: OutputCallback, stderr_cb: OutputCallback):
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    await asyncio.gather(
        _read_stream(process.stdout, stdout_cb), _read_stream(process.stderr, stderr_cb)
    )
    return await process.wait()


def _prepare_output(
    spec: OutputHandler, default_level=logging.INFO, default_name=None
) -> OutputCallback:
    if isinstance(spec, LoggerSpec):
        if spec is None:
            spec = default_name
        return proc_logger(spec, default_level)
    else:
        return spec


def execute(
    cmd: Sequence[str],
    stdout: OutputHandler | None = None,
    stdout_level: int = logging.INFO,
    stderr: OutputHandler | None = None,
    stderr_level: int = logging.WARNING,
) -> int:
    """
    Run the given command and log its output as it appears.
    """
    stdout_cb = _prepare_output(stdout, default_name=cmd[0], default_level=stdout_level)
    stderr_cb = _prepare_output(stderr, default_name=cmd[0], default_level=stderr_level)
    loop = asyncio.get_event_loop()
    rc = loop.run_until_complete(_stream_subprocess(cmd, stdout_cb, stderr_cb))
    return rc
