from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.pages.config import load_beeui_config
from beeui_module.pages.locale import translate
from beeui_module.web.app import create_beeui_app


def test_locale_lang_query_updates_html_lang() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=ru")

    assert response.status_code == 200
    assert '<html lang="ru"' in response.text


def test_locale_invalid_lang_falls_back_to_default_html_lang() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=bad")

    assert response.status_code == 200
    assert '<html lang="en"' in response.text


def test_locale_resolved_page_title_renders_from_query(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title:\n"
        "    en: BeeUI\n"
        "    ru: БИУ\n"
        "  product: test\n"
        "  logo_text:\n"
        "    en: BeeUI\n"
        "    ru: БИУ\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title:\n"
        "      en: Dashboard\n"
        "      ru: Дашборд\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title:\n"
        "      en: Dashboard\n"
        "      ru: Дашборд\n"
        "    subtitle:\n"
        "      en: Demo\n"
        "      ru: Демо\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      items:\n"
        "        - id: overview\n"
        "          title:\n"
        "            en: Overview\n"
        "            ru: Обзор\n"
        "          href: /?tab=overview\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    en_response = client.get("/")
    ru_response = client.get("/?lang=ru")

    assert en_response.status_code == 200
    assert ru_response.status_code == 200

    assert "Dashboard" in en_response.text
    assert "Дашборд" in ru_response.text
    assert "Demo" in en_response.text
    assert "Демо" in ru_response.text
    assert "Overview" in en_response.text
    assert "Обзор" in ru_response.text
    assert "BeeUI" in en_response.text
    assert "БИУ" in ru_response.text


def test_locale_invalid_lang_falls_back_to_default(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title:\n"
        "    en: BeeUI\n"
        "    ru: БИУ\n"
        "  product: test\n"
        "  logo_text: BeeUI\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=bad")
    assert response.status_code == 200
    assert "Dashboard" in response.text
    assert '<html lang="en"' in response.text


def test_language_switcher_renders_with_multiple_locales(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: BeeUI\n"
        "  product: test\n"
        "  logo_text: BeeUI\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert 'class="beeui-language-switcher"' in response.text
    assert "EN" in response.text
    assert "RU" in response.text


def test_language_switcher_not_rendered_with_single_locale(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: BeeUI\n"
        "  product: test\n"
        "  logo_text: BeeUI\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert 'class="beeui-language-switcher"' not in response.text


def test_language_switcher_href_preserves_current_path_and_replaces_lang(
    tmp_path: Path,
) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: BeeUI\n"
        "  product: test\n"
        "  logo_text: BeeUI\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=en&period=7d")
    assert response.status_code == 200
    assert "beeui-language-switcher" in response.text
    assert "lang=ru" in response.text
    assert "period=7d" in response.text
    assert "beeui-lang-active" in response.text
    assert 'beeui-lang-active">EN<' in response.text


def test_language_switcher_href_does_not_include_unknown_params(
    tmp_path: Path,
) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: BeeUI\n"
        "  product: test\n"
        "  logo_text: BeeUI\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=en&evil=yes&secret=bad")
    assert response.status_code == 200
    assert "secret" not in response.text
    assert "evil" not in response.text
    assert "Ru" not in response.text


def test_component_catalog_locale_works(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title:\n"
        "    en: BeeUI\n"
        "    ru: БИУ\n"
        "  product: test\n"
        "  logo_text:\n"
        "    en: BeeUI\n"
        "    ru: БИУ\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    ru_response = client.get("/components?lang=ru")
    assert ru_response.status_code == 200
    assert "beeui-language-switcher" in ru_response.text
    assert "БИУ" in ru_response.text
    assert "{'en':" not in ru_response.text
    assert "lang=ru" in ru_response.text


def test_invalid_lang_not_preserved_in_nav_hrefs(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: BeeUI\n"
        "  product: test\n"
        "  logo_text: BeeUI\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=bad")
    assert response.status_code == 200
    assert "lang=bad" not in response.text


def test_page_tabs_do_not_preserve_invalid_lang_or_empty_params(
    tmp_path: Path,
) -> None:
    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: BeeUI\n"
        "  product: test\n"
        "  logo_text: BeeUI\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    tabs:\n"
        "      items:\n"
        "        - id: overview\n"
        "          title:\n"
        "            en: Overview\n"
        "            ru: Обзор\n"
        "          href: /?tab=overview\n"
        "        - id: details\n"
        "          title:\n"
        "            en: Details\n"
        "            ru: Детали\n"
        "          href: /?tab=details\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?tab=overview&lang=bad&period=&run_id=")

    assert response.status_code == 200
    assert "lang=bad" not in response.text
    assert "period=" not in response.text
    assert "run_id=" not in response.text


def test_component_catalog_index_link_preserves_lang() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/components/interface?lang=ru")

    assert response.status_code == 200
    assert 'href="/components?lang=ru"' in response.text


def test_beeui_translation_catalog_uses_configured_default_and_safe_fallback() -> None:
    assert translate("filter.columns", "en") == "Columns"
    assert translate("filter.columns", "ru") == "Колонки"
    assert translate("chart.error", "unknown", "ru") == "Ошибка рендеринга графика"
    assert translate("unknown.key", "ru") == "unknown.key"
    assert translate("detail.show_text", "ru") == "Показать текст"
    assert translate("detail.close", "ru") == "Закрыть"


def test_mounted_locale_cookie_uses_effective_boundary_path() -> None:
    from fastapi import FastAPI

    from beeui_module.web.app import mount_beeui

    root = TestClient(create_beeui_app())
    root_response = root.get("/?lang=ru")
    assert "Path=/" in root_response.headers["set-cookie"]

    prefixed_settings = load_settings(settings_path())
    prefixed_settings["web"] = dict(prefixed_settings["web"])
    prefixed_settings["web"]["route_prefix"] = "/ui"
    prefixed = TestClient(create_beeui_app(settings=prefixed_settings))
    prefixed_response = prefixed.get("/ui/?lang=ru")
    assert "Path=/ui" in prefixed_response.headers["set-cookie"]

    parent = FastAPI()
    mount_beeui(parent, path="/ui")
    client = TestClient(parent)

    valid = client.get("/ui/?lang=ru")
    assert valid.status_code == 200
    assert "beeui_lang=ru" in valid.headers["set-cookie"]
    assert "Path=/ui" in valid.headers["set-cookie"]
    assert "SameSite=lax" in valid.headers["set-cookie"]

    invalid = client.get("/ui/?lang=fr")
    assert invalid.status_code == 200
    assert "beeui_lang" not in invalid.headers.get("set-cookie", "")
