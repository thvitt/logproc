from random import randint, random
import pytest
import asyncio
import logging
from logproc import aexecute, execute, map_unordered


def test_defaults(caplog):
    caplog.clear()
    with caplog.at_level(logging.INFO):
        exitcode = execute(
            [
                "bash",
                "-c",
                "echo stdout && sleep 0.01 && echo stderr 1>&2 && sleep 0.01 && echo done",
            ],
        )
        assert exitcode == 0
        assert caplog.records[0].levelname == "INFO", caplog.records[0]
        assert caplog.records[0].message == "stdout"
        assert caplog.records[1].levelname == "WARNING"
        assert caplog.records[1].message == "stderr"
        assert caplog.records[2].levelname == "INFO"


@pytest.mark.asyncio
async def test_map_unordered_simple():
    async def worker(x):
        await asyncio.sleep(0.01 * (5 - x))
        return x * x

    results = []
    async for result in map_unordered(worker, range(5)):
        results.append(result)

    assert sorted(results) == [0, 1, 4, 9, 16]


@pytest.mark.asyncio
async def test_map_unordered_aexecute(caplog):
    commands = []
    for i in range(5):
        t = randint(1, 5) / 10
        commands.append(
            [
                "/bin/bash",
                "-c",
                f"sleep {t}; echo 'Task {i}: slept {t} seconds'; exit {i}",
            ]
        )

    caplog.clear()
    with caplog.at_level(logging.INFO):
        results = [result async for result in map_unordered(aexecute, commands)]

    assert sorted(results) == [0, 1, 2, 3, 4]
    for i in range(5):
        assert "Task" in caplog.records[i].message, caplog.records[i]
