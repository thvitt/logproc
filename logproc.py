"""
Run a process and log stdin and stdout.

This experimental module offers a function `execute()` that runs a commandline
in a subprocess and separately live captures the called process’s standard
output and standard error. By default, the output is logged at different
levels, but it is possible to provide a callback for different handling.
"""

__version__ = "0.3.0"


import asyncio
from collections.abc import Callable, Sequence
import logging

OutputCallback = Callable[[str | bytes], None]
"""
A callback that receives a line of output as str or bytes. You can use `proc_logger` to create typical variants.
"""

LoggerSpec = str | logging.Logger | None
"""
A logger, a logger name, or None to indicate a logger inferred from context.
"""

OutputHandler = OutputCallback | LoggerSpec
"""
Something that can handle output: either a callback or a logger spec.
"""


def proc_logger(
    prefix: str = "", level: int = logging.INFO, logger: LoggerSpec = None, extra=None
) -> OutputCallback:
    """
    Creates a callback for execute() that logs to a logger.

    Args:
        prefix: String that will be prepended to each line
        logger: If given, this is either a logger or the name of a logger.
                If missing, we log to the root logger.
        level: The level at which to log the messages.
    """
    if logger is None:
        logger = logging.getLogger()
    elif isinstance(logger, str):
        logger = logging.getLogger(logger)

    def log(line: bytes | str):
        if isinstance(line, bytes):
            line = line.decode(errors="replace").rstrip()
        logger.log(level, prefix + line, stacklevel=10, extra=extra)

    return log


async def _read_stream(stream, cb: OutputCallback):
    while line := await stream.readline():
        cb(line)


async def _stream_subprocess(
    cmd, stdout_cb: OutputCallback, stderr_cb: OutputCallback, cwd=None
) -> int:
    """
    Runs the process asynchronously and wait until it is finished. When the
    process produces output, the given callbacks are called with each line.
    """
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd
    )

    await asyncio.gather(
        _read_stream(process.stdout, stdout_cb), _read_stream(process.stderr, stderr_cb)
    )
    return await process.wait()


def _prepare_output(
    spec: OutputHandler,
    default_level=logging.INFO,
    default_name: str | None = None,
    prefix: str = "",
) -> OutputCallback:
    if callable(spec):
        return spec
    else:
        if spec is None:
            spec = default_name
        return proc_logger(level=default_level, logger=spec, prefix=prefix)


def execute(
    cmd: Sequence[str],
    stdout: OutputHandler | None = None,
    stdout_level: int = logging.INFO,
    stderr: OutputHandler | None = None,
    stderr_level: int = logging.WARNING,
    cwd=None,
    prefix: str = "",
) -> int:
    """
    Run the given command and log its output as it appears, blocking while the program runs.

    Description:
        `execute` runs the given command and waits for it to finish. While it
        is running, its stdout and stderr streams are monitored. Each new line
        appearing on these streams are immediately handled.

        The default handlers will log the message from the subprocess to a
        logger that logs using the first member of the cmd sequence as a logger
        name and logging.INFO for stdout and logging.WARNING for stderr output.

    Args:
        cmd: A list of arguments, as in subprocess.run etc.
        stdout: Handlers for the standard output stream. Each of these can be:

            - None (the default) to use the default settings
            - a logger name
            - a `logging.Logger`
            - a callback that receives a line as `str` or `bytes` as argument and handles that

        stderr: Like stdout, but for standard error.
        stdout_level:
        stderr_level: Logging levels for the specific output.
        prefix: A string that is prepended to each line before logging.
    Returns:
        the command’s exit code

    See also:
        aexecute()

    """
    rc = asyncio.run(
        aexecute(cmd, stdout, stdout_level, stderr, stderr_level, cwd, prefix)
    )
    return rc


async def aexecute(
    cmd: Sequence[str],
    stdout: OutputHandler | None = None,
    stdout_level: int = logging.INFO,
    stderr: OutputHandler | None = None,
    stderr_level: int = logging.WARNING,
    cwd=None,
    prefix: str = "",
) -> int:
    """
    Asynchronously run the given command and log its output as it appears.

    Description:
        `aexecute` runs the given command and waits for it to finish. While it
        is running, its stdout and stderr streams are monitored. Each new line
        appearing on these streams are immediately handled.

        The default handlers will log the message from the subprocess to a
        logger that logs using the first member of the cmd sequence as a logger
        name and logging.INFO for stdout and logging.WARNING for stderr output.

    Args:
        cmd: A list of arguments, as in subprocess.run etc.
        stdout: Handlers for the standard output stream. Each of these can be:

            - None (the default) to use the default settings
            - a logger name
            - a `logging.Logger`
            - a callback that receives a line as `str` or `bytes` as argument and handles that

        stderr: Like stdout, but for standard error.
        stdout_level:
        stderr_level: Logging levels for the specific output.
        prefix: A string that is prepended to each line before logging.
    Returns:
        the command’s exit code
    """
    stdout_cb = _prepare_output(
        stdout, default_name=cmd[0], default_level=stdout_level, prefix=prefix
    )
    stderr_cb = _prepare_output(
        stderr, default_name=cmd[0], default_level=stderr_level, prefix=prefix
    )
    return await _stream_subprocess(cmd, stdout_cb, stderr_cb, cwd=cwd)
