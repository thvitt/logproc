import logging
from logproc import execute


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
