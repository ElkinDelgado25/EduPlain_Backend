import os

from config.settings.env_loader import load_local_env_files


def test_development_env_local_overrides_env_without_replacing_process_env(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.delenv("VALUE_FROM_ENV", raising=False)
    monkeypatch.setenv("VALUE_FROM_PROCESS", "process")

    (tmp_path / ".env").write_text(
        "VALUE_FROM_ENV=base\nVALUE_FROM_LOCAL=base\nVALUE_FROM_PROCESS=base\n",
        encoding="utf-8",
    )
    (tmp_path / ".env.local").write_text(
        "VALUE_FROM_LOCAL=local\nVALUE_FROM_PROCESS=local\n",
        encoding="utf-8",
    )

    load_local_env_files(tmp_path)

    assert os.environ["VALUE_FROM_ENV"] == "base"
    assert os.environ["VALUE_FROM_LOCAL"] == "local"
    assert os.environ["VALUE_FROM_PROCESS"] == "process"
