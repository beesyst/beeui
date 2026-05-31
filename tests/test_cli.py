from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

from beeui_module.cli.doctor import run_doctor
from beeui_module.cli.main import main
from beeui_module.core.log import configure_logging
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version

REPO_ROOT = Path(__file__).resolve().parents[1]


# Тест: команда doctor вызывается через main
def test_main_dispatches_doctor(monkeypatch) -> None:
    calls: list[str] = []

    def fake_run_doctor() -> int:
        calls.append("doctor")
        return 0

    monkeypatch.setattr("beeui_module.cli.main.run_doctor", fake_run_doctor)

    assert main(["doctor"]) == 0
    assert calls == ["doctor"]


# Тест: чек вывода маршрутов через CLI
def test_main_prints_routes(capsys) -> None:
    assert main(["routes"]) == 0

    captured = capsys.readouterr()
    assert "Configured route surface:" in captured.out
    assert "GET /" in captured.out
    assert "GET /runs" in captured.out
    assert "GET /health" in captured.out
    assert "GET /static/..." in captured.out


# Тест: чек обработки неизвестной команды и вывода ошибки
def test_invalid_command_is_handled_safely(capsys) -> None:
    assert main(["bogus"]) == 2

    captured = capsys.readouterr()
    assert "Unknown command: bogus" in captured.err


# Тест: стартовый скрипт выводит версию
def test_start_script_dispatches_version() -> None:
    result = subprocess.run(
        [sys.executable, "config/start.py", "version"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == f"beeui {get_version()}"


# Тест: чек, что команда doctor пишет в stdout и создает лог-файл с ожидаемым содержимым
def test_doctor_writes_stdout_and_log(tmp_path, capsys) -> None:
    root = tmp_path
    (root / "config").mkdir()
    (root / "logs").mkdir()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "beeui"\nversion = "0.1.0"\n', encoding="utf-8"
    )
    (root / "config" / "settings.yml").write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "  cache_static: 60\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )
    (root / "config" / "schema.yml").write_text(
        "app:\n"
        "  title: BeeUI Demo\n"
        "  product: demo\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo operator dashboard\n"
        "    blocks: []\n",
        encoding="utf-8",
    )

    assert run_doctor(root=root) == 0

    captured = capsys.readouterr()
    assert "beeui doctor: ok" in captured.out
    assert (root / "logs" / "app.log").is_file()


# Тест: web-команда передает аргументы в run_web
def test_main_dispatches_web_args(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run_web(args) -> int:
        calls.append(list(args))
        return 0

    monkeypatch.setattr("beeui_module.cli.main.run_web", fake_run_web)

    assert main(["web", "--host", "127.0.0.1", "--port", "8780"]) == 0
    assert calls == [["--host", "127.0.0.1", "--port", "8780"]]


# Тест: чек, что старая команда serve больше не поддерживается и вызывает ошибку
def test_old_serve_command_is_not_supported(capsys) -> None:
    assert main(["serve"]) == 2

    captured = capsys.readouterr()
    assert "Unknown command: serve" in captured.err


# Тест: load_settings читает валидный конфиг
def test_load_settings_reads_valid_config(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "  cache_static: 60\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    settings = load_settings(config_path)

    assert settings["app"]["name"] == "beeui"
    assert settings["logging"]["level"] == "INFO"
    assert settings["storage"]["root"] == "storage"


# Тест: отсутствие logging.level вызывает fail-fast ошибку
def test_load_settings_fails_fast_on_missing_logging_level(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "  cache_static: 60\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "Missing required key: logging.level"
    else:
        raise AssertionError(
            "load_settings must fail fast when logging.level is missing"
        )


# Тест: чек, что configure_logging создает лог-файл с ожидаемым содержимым
def test_configure_logging_creates_configured_log_file(tmp_path) -> None:
    root = tmp_path
    (root / "pyproject.toml").write_text(
        '[project]\nname = "beeui"\nversion = "0.1.0"\n', encoding="utf-8"
    )

    logger = configure_logging(
        root=root,
        level="INFO",
        utc=True,
        clear_logs=True,
        log_file="logs/app.log",
    )
    logger.info("configured log file smoke")

    log_path = root / "logs" / "app.log"
    assert log_path.is_file()
    assert "configured log file smoke" in log_path.read_text(encoding="utf-8")

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(logging.NOTSET)
