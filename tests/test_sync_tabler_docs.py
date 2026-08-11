from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_command(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        check=False,
        text=True,
    )


def create_upstream(root: Path) -> tuple[Path, str]:
    upstream = root / "upstream"
    (upstream / "docs").mkdir(parents=True)
    (upstream / "docs" / "index.mdx").write_text("new docs\n", encoding="utf-8")
    (upstream / "LICENSE").write_text("new license\n", encoding="utf-8")
    assert run_command("git", "init", "-q", cwd=upstream).returncode == 0
    assert run_command("git", "add", "docs", "LICENSE", cwd=upstream).returncode == 0
    assert (
        run_command(
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "initial docs",
            cwd=upstream,
        ).returncode
        == 0
    )
    assert run_command("git", "branch", "-M", "dev", cwd=upstream).returncode == 0
    commit = run_command("git", "rev-parse", "HEAD", cwd=upstream)
    assert commit.returncode == 0
    return upstream, commit.stdout.strip()


def create_sync_fixture(root: Path) -> Path:
    fixture = root / "beeui"
    script_directory = fixture / "scripts"
    destination = fixture / "docs" / "vendor" / "tabler"
    script_directory.mkdir(parents=True)
    destination.mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "scripts" / "sync_tabler_docs.sh", script_directory)
    (destination / "README.md").write_text("BeeUI-owned README\n", encoding="utf-8")
    (destination / "LICENSE").write_text("old license\n", encoding="utf-8")
    (destination / "UPSTREAM_REF").write_text("old-ref\n", encoding="utf-8")
    (destination / "UPSTREAM_COMMIT").write_text("old-commit\n", encoding="utf-8")
    (destination / "content").mkdir()
    (destination / "content" / "old.md").write_text("old docs\n", encoding="utf-8")
    return fixture


def snapshot(destination: Path) -> dict[str, bytes]:
    return {
        path.relative_to(destination).as_posix(): path.read_bytes()
        for path in sorted(destination.rglob("*"))
        if path.is_file()
    }


def sync(
    fixture: Path,
    upstream: Path,
    ref: str = "dev",
    environment_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ | {
        "TABLER_REPOSITORY": upstream.as_uri(),
        "TABLER_REF": ref,
    }
    if environment_overrides is not None:
        environment |= environment_overrides
    return subprocess.run(
        ["bash", "scripts/sync_tabler_docs.sh"],
        cwd=fixture,
        capture_output=True,
        check=False,
        env=environment,
        text=True,
    )


def test_sync_tabler_docs_stages_and_preserves_unmanaged_files(
    tmp_path: Path,
) -> None:
    upstream, commit = create_upstream(tmp_path)
    fixture = create_sync_fixture(tmp_path)

    result = sync(fixture, upstream)

    destination = fixture / "docs" / "vendor" / "tabler"
    assert result.returncode == 0, result.stderr
    assert (destination / "content" / "index.mdx").read_text(
        encoding="utf-8"
    ) == "new docs\n"
    assert not (destination / "content" / "old.md").exists()
    assert (destination / "LICENSE").read_text(encoding="utf-8") == "new license\n"
    assert (destination / "UPSTREAM_REF").read_text(encoding="utf-8") == "dev\n"
    assert (destination / "UPSTREAM_COMMIT").read_text(
        encoding="utf-8"
    ) == f"{commit}\n"
    assert (destination / "README.md").read_text(
        encoding="utf-8"
    ) == "BeeUI-owned README\n"
    assert not list(destination.glob(".tabler-sync-*"))


def test_sync_tabler_docs_missing_source_preserves_snapshot(
    tmp_path: Path,
) -> None:
    upstream, _ = create_upstream(tmp_path)
    fixture = create_sync_fixture(tmp_path)
    destination = fixture / "docs" / "vendor" / "tabler"
    assert (
        run_command(
            "git", "checkout", "--orphan", "missing-docs", cwd=upstream
        ).returncode
        == 0
    )
    assert run_command("git", "rm", "-rf", ".", cwd=upstream).returncode == 0
    (upstream / "LICENSE").write_text("missing docs license\n", encoding="utf-8")
    assert run_command("git", "add", "LICENSE", cwd=upstream).returncode == 0
    assert (
        run_command(
            "git",
            "-c",
            "user.name=Test User",
            "-c",
            "user.email=test@example.invalid",
            "commit",
            "-qm",
            "missing docs",
            cwd=upstream,
        ).returncode
        == 0
    )
    before = snapshot(destination)

    result = sync(fixture, upstream, "missing-docs")

    assert result.returncode != 0
    assert "Expected documentation directory 'docs' is absent" in result.stderr
    assert snapshot(destination) == before
    assert not list(destination.glob(".tabler-sync-*"))


def test_sync_tabler_docs_backup_failure_preserves_snapshot(tmp_path: Path) -> None:
    upstream, _ = create_upstream(tmp_path)
    fixture = create_sync_fixture(tmp_path)
    destination = fixture / "docs" / "vendor" / "tabler"
    command_directory = tmp_path / "commands"
    command_directory.mkdir()
    mv_path = shutil.which("mv")
    assert mv_path is not None
    (command_directory / "mv").write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"${1##*/}\" == \"UPSTREAM_REF\" && \"${2##*/}\" == \"UPSTREAM_REF\" ]]; then\n"
        "  exit 1\n"
        "fi\n"
        f"exec {mv_path} \"$@\"\n",
        encoding="utf-8",
    )
    (command_directory / "mv").chmod(0o755)
    before = snapshot(destination)

    result = sync(
        fixture,
        upstream,
        environment_overrides={
            "PATH": f"{command_directory}{os.pathsep}{os.environ['PATH']}",
        },
    )

    assert result.returncode != 0
    assert snapshot(destination) == before
    assert not list(destination.glob(".tabler-sync-*"))


def test_sync_tabler_docs_is_idempotent_for_one_commit(
    tmp_path: Path,
) -> None:
    upstream, _ = create_upstream(tmp_path)
    fixture = create_sync_fixture(tmp_path)
    destination = fixture / "docs" / "vendor" / "tabler"
    assert sync(fixture, upstream).returncode == 0
    first_snapshot = snapshot(destination)

    result = sync(fixture, upstream)

    assert result.returncode == 0, result.stderr
    assert snapshot(destination) == first_snapshot
    assert not list(destination.glob(".tabler-sync-*"))
