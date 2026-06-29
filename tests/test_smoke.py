from __future__ import annotations


def test_import_smoke() -> None:
    import beeui_module

    assert beeui_module is not None
