# logproc

Run a process and log stdin and stdout.

## Description

This experimental module offers a function execute() that runs a commandline
in a subprocess and separately live captures the called process’s standard
output and standard error. By default, the output is logged at different
levels, but it is possible to provide a callback for different handling.

## Usage

In the simplest case, just run `execute(["ls", "-l"])`, which will run `ls -l`
and log its output with Python’s default logging system, using the logger id
`ls` and the level INFO for stdout, WARNING for stderr.

If you need further customization, here are the two API functions of
this module:

### execute

```python
def execute(cmd: Sequence[str],
            stdout: OutputHandler | None = None,
            stdout_level: int = logging.INFO,
            stderr: OutputHandler | None = None,
            stderr_level: int = logging.WARNING,
            cwd=None) -> int
```

Run the given command and log its output as it appears.

#### Arguments

- `cmd` - A list of arguments, as in subprocess.run etc.
- stdout, stderr:
  Handlers for the specified stream. Each of these can be:

  - None (the default) to use the default settings
  - a logger name
  - a `logging.Logger`
  - a callback

  You can use `proc_logger` to build a suitable callback.

- stdout_level, stderr_level: Logging levels for the specific output.

#### Returns

the command’s exit code
  
#### Description
  
`execute` runs the given command and waits for it to finish. While it
is running, its stdout and stderr streams are monitored. Each new line
appearing on these streams are immediately handled.

The default handlers will log the message from the subprocess to a
logger that logs using the first member of the cmd sequence as a logger
name and logging.INFO for stdout and logging.WARNING for stderr output.

### proc\_logger

```python
def proc_logger(prefix: str = "",
                level: int = logging.INFO,
                logger: LoggerSpec = None,
                extra=None) -> OutputCallback
```

Creates a callback for execute() that logs to a logger.

#### Arguments

- `prefix` - String that will be prepended to each line
- `logger` - If given, this is either a logger or the name of a logger.
  If missing, we log to the root logger.
- `level` - The level at which to log the messages.
- `extra` - an optional dictionary with extra attributes that gets past on with each log entry
