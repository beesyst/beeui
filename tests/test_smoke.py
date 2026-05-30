from __future__ import annotations


# Тест: базовый smoke test для проверки импорта основных компонентов без ошибок
def test_import_smoke() -> None:
    import beeui_module

    assert beeui_module is not None
