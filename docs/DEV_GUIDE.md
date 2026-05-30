# DEV_GUIDE — запуск, логи, интеграции, SDLC-light

## Purpose

Этот документ описывает:

- как запускать `beeui`;
- как работать с окружением и зависимостями;
- где смотреть логи и runtime/demo artifacts;
- как подключать `beeui` к `beecap`, `beeagent` и будущим Bee-продуктам;
- как вести разработку в рамках текущего SDLC-light процесса;
- как формулировать задачи для Copilot / AI так, чтобы изменения были консистентны с архитектурой проекта, `docs/ROADMAP.md`, `docs/SDLC.md` и `docs/SECURITY.md`.

## Related project docs

Этот документ используется вместе с:

- `docs/ROADMAP.md` — этапы, итерации, scope, checks, DoD;
- `docs/SDLC.md` — lightweight process, change levels, required checks, PR flow;
- `docs/SECURITY.md` — secure development rules и security checks по типу изменения;
- `docs/INTEGRATION.md` — как подключать `beeui` к Bee-продуктам;
- `docs/COMPONENTS.md` — reusable blocks/components contract;
- `docs/API_CONTRACT.md` — JSON API envelopes and route contracts;
- `docs/WEB_UI.md` — HTML routes, layout, dashboard behavior;
- `docs/THEME.md` — theme/customization contract.

Правило:

> `DEV_GUIDE` не заменяет `ROADMAP`, `SDLC` и `SECURITY`, а помогает разработчику быстро применять их на практике.

## Что такое `beeui`

`beeui` — reusable Python-based UI layer для Bee-продуктов.

Он предоставляет:

- FastAPI + Jinja2 + Tabler web surface;
- declarative pages and dashboard blocks;
- product adapters for `beecap`, `beeagent` and future Bee products;
- artifact browser and source links;
- stable read-only JSON API contracts;
- bounded config/admin/operator controls;
- theme/customization layer;
- future foundation for no-code dashboard/frontend builder.

Главное правило:

> BeeUI renders. Product decides.

Это означает:

- `beeui` не должен содержать trading logic `beecap`;
- `beeui` не должен содержать agent/capability policy logic `beeagent`;
- `beeui` не должен напрямую исполнять broker/runtime/product actions;
- product-specific semantics должны жить в product adapter/read-model layer.

## Требования

- Python 3.12+
- `uv`
- Git
- локально клонированные Bee-проекты, если нужна интеграция:

```text
~/Projects/
  beeui/
  beecap/
  beeagent/
```

## Рекомендуемая workspace-структура

`beeui` должен быть отдельной репой:

```text
~/Projects/beeui
```

Не нужно вкладывать `beeui` внутрь `beecap` или `beeagent`.

Рекомендуемый VS Code multi-root workspace:

```json
{
  "folders": [
    { "name": "beeui", "path": "/home/bee/Projects/beeui" },
    { "name": "beecap", "path": "/home/bee/Projects/beecap" },
    { "name": "beeagent", "path": "/home/bee/Projects/beeagent" }
  ],
  "settings": {
    "python.analysis.extraPaths": [
      "/home/bee/Projects/beeui/src",
      "/home/bee/Projects/beecap/src",
      "/home/bee/Projects/beeagent/src"
    ]
  }
}
```

Архитектурно проекты остаются отдельными. Workspace нужен только для удобства разработки.

## Установка и зависимости (`uv`)

В проекте используется `uv`.

Источник правды:

- `pyproject.toml` — список зависимостей и constraints;
- `uv.lock` — точные зафиксированные версии для воспроизводимой установки.

`uv.lock` коммитится в репозиторий и не добавляется в `.gitignore`.

### Обычный запуск

Основной entrypoint:

```bash
./start.sh
```

`start.sh` делает:

- проверяет наличие `uv`;
- если `uv` отсутствует — устанавливает его;
- ставит недостающие зависимости из `uv.lock`;
- подключает `dev` extra, чтобы локальные тесты работали без отдельной подготовки;
- запускает `config/start.py`;
- не изменяет `uv.lock`.

Правило:

> Обычный запуск `./start.sh` не должен менять `pyproject.toml` или `uv.lock`.

Если после обычного запуска изменился `uv.lock`, это проблема dependency workflow. Её нужно исправить до PR.

### Рекомендуемый `start.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "[install] uv не найден, устанавливаю..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

uv sync --frozen --extra dev

uv run --frozen --extra dev python config/start.py "$@"
```

## Тесты

После `./start.sh` можно запускать тесты:

```bash
uv run pytest -q
```

Для frozen-проверки:

```bash
uv run --frozen --extra dev pytest -q
```

## Добавить runtime-зависимость

Правильный способ — через `uv add`, а не ручным редактированием `pyproject.toml`:

```bash
uv add <package>
./start.sh
uv run pytest -q
git status
```

Коммитить нужно оба файла:

```bash
git add pyproject.toml uv.lock
git commit -m "chore(deps): add <package>"
```

Пример:

```bash
uv add fastapi
./start.sh
uv run pytest -q
git add pyproject.toml uv.lock
git commit -m "chore(deps): add fastapi"
```

## Добавить dev-зависимость

Dev-зависимости оформляются как optional extra `dev`:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "httpx>=0.28",
]
```

Добавлять dev-зависимость нужно так:

```bash
uv add --optional dev <package>
./start.sh
uv run pytest -q
git status
```

Коммитить нужно оба файла:

```bash
git add pyproject.toml uv.lock
git commit -m "chore(deps): add <package>"
```

Пример:

```bash
uv add --optional dev pytest-mock
./start.sh
uv run pytest -q
git add pyproject.toml uv.lock
git commit -m "chore(deps): add pytest-mock"
```

## Добавить docs-зависимость

Docs-зависимости оформляются как optional extra `docs`:

```toml
[project.optional-dependencies]
docs = [
    "mkdocs>=1.6,<2.0",
    "mkdocs-material>=9.6,<10.0",
]
```

Добавлять docs-зависимость нужно так:

```bash
uv add --optional docs <package>
uv sync --frozen --extra docs
uv run --frozen --extra docs mkdocs build --strict
git status
```

Коммитить нужно оба файла:

```bash
git add pyproject.toml uv.lock
git commit -m "chore(deps): add docs dependency"
```

## Если зависимость добавлена руками в `pyproject.toml`

Ручное редактирование допустимо, но после него обязательно обнови lockfile:

```bash
uv lock
./start.sh
uv run pytest -q
git status
```

Коммитить нужно оба файла:

```bash
git add pyproject.toml uv.lock
git commit -m "chore(deps): update dependencies"
```

## Удалить зависимость

```bash
uv remove <package>
./start.sh
uv run pytest -q
git status
```

Коммитить нужно оба файла:

```bash
git add pyproject.toml uv.lock
git commit -m "chore(deps): remove <package>"
```

## Обновить конкретную зависимость

```bash
uv lock --upgrade-package <package>
./start.sh
uv run pytest -q
git status
```

Если менялся только lockfile:

```bash
git add uv.lock
git commit -m "chore(deps): update <package>"
```

Если вместе с этим менялся `pyproject.toml`, коммитить оба файла:

```bash
git add pyproject.toml uv.lock
git commit -m "chore(deps): update <package>"
```

## Обновить все зависимости

Массовый апгрейд делай отдельным PR, не смешивай с feature/fix задачами:

```bash
uv lock --upgrade
./start.sh
uv run pytest -q
git status
```

Коммит:

```bash
git add uv.lock
git commit -m "chore(deps): update locked dependencies"
```

## Локальный preview docs

Если подключены docs-зависимости:

```bash
uv sync --frozen --extra docs
uv run --frozen --extra docs mkdocs serve
```

Strict build:

```bash
uv sync --frozen --extra docs
uv run --frozen --extra docs mkdocs build --strict
```

## Базовая шпаргалка

| Ситуация                          | Команды                                                                                                     |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Обычный запуск                    | `./start.sh`                                                                                                |
| Doctor                            | `./start.sh doctor`                                                                                         |
| Web demo                          | `./start.sh serve --host 127.0.0.1 --port 8780`                                                             |
| Тесты после запуска               | `uv run pytest -q`                                                                                          |
| Добавить runtime-зависимость      | `uv add <package>` → `./start.sh` → `uv run pytest -q` → commit `pyproject.toml` + `uv.lock`                |
| Добавить dev-зависимость          | `uv add --optional dev <package>` → `./start.sh` → `uv run pytest -q` → commit `pyproject.toml` + `uv.lock` |
| Ручное изменение `pyproject.toml` | `uv lock` → `./start.sh` → `uv run pytest -q` → commit `pyproject.toml` + `uv.lock`                         |
| Удалить зависимость               | `uv remove <package>` → `./start.sh` → `uv run pytest -q` → commit `pyproject.toml` + `uv.lock`             |
| Обновить пакет                    | `uv lock --upgrade-package <package>` → `./start.sh` → `uv run pytest -q` → commit `uv.lock`                |

---

## Что нельзя делать

Не делай так в `start.sh`:

```bash
uv sync --extra dev
```

Причина: обычный запуск не должен пересобирать `uv.lock`.

Не добавляй `uv.lock` в `.gitignore`.

Причина: `uv.lock` нужен для одинаковых версий зависимостей у всех разработчиков, CI и runtime.

Не добавляй CDN-зависимости без явной причины.

Причина: `beeui` должен быть пригоден для локального/internal deployment без внешних runtime-зависимостей на CDN.

Не копируй Tabler demo HTML целиком без чистки.

Причина: demo templates могут содержать demo-only скрипты, tracking snippets, лишние examples и нецелевой markup.

## Настройка

Главный config для demo/development:

```text
config/demo.beeui.yml
```

Позже product-specific config:

```text
beecap/config/beeui.yml
beeagent/config/beeui.yml
```

### Правило по конфигу

`beeui.yml` — source of truth для UI layout, pages, navigation, blocks and theme.

Это означает:

- pages не должны “магически” появляться из кода без schema/config;
- обязательные keys должны валидироваться fail-fast;
- если обязательного ключа нет — приложение должно падать с понятной ошибкой на старте;
- product-specific data semantics не должны попадать в generic block renderer.

### Что должно жить в `beeui.yml`

- app title/product id;
- theme;
- navigation;
- pages;
- layout;
- block declarations;
- data source references;
- optional auth/config UI/action declarations.

### Что не должно жить в `beeui.yml`

- secrets;
- broker credentials;
- trading logic;
- product runtime policy;
- hidden execution authority;
- arbitrary Python code;
- arbitrary HTML/JS templates от пользователя.

## Правило по секретам

Секреты и env-sensitive значения:

- не должны хардкодиться в коде;
- не должны попадать в HTML/API/logs/artifacts;
- не должны передаваться в Jinja context без redaction;
- не должны отображаться в config read-model;
- не должны быть editable через config UI;
- требуют extra attention для изменений уровня `security-sensitive` по `docs/SECURITY.md`.

Для `beeui` особенно чувствительны:

- auth/session secrets;
- cookie signing keys;
- product API tokens;
- filesystem paths;
- artifact read paths;
- config apply payloads;
- action payloads.

## Запуск

Основной запуск:

```bash
./start.sh
```

По умолчанию допустимо, чтобы `./start.sh` запускал `doctor` или default demo command. Конкретное поведение фиксируется в `config/start.py`.

### Прямой запуск через `uv`

```bash
uv sync --frozen --extra dev
uv run --frozen --extra dev python config/start.py
```

Для конкретной CLI-команды:

```bash
uv run --frozen --extra dev python config/start.py doctor
uv run --frozen --extra dev python config/start.py serve --host 127.0.0.1 --port 8780
```

В обычной разработке предпочтительный entrypoint — `./start.sh`.

## CLI entrypoints

Текущий целевой набор команд по мере развития:

```bash
./start.sh doctor
./start.sh serve --config config/demo.beeui.yml --host 127.0.0.1 --port 8780
```

Будущие команды:

```bash
./start.sh validate --config config/demo.beeui.yml
./start.sh inspect-config --config config/demo.beeui.yml
./start.sh build-static-assets
```

Правило:

> Изменение должно проверяться через тот entrypoint или CLI, который соответствует его реальному поведению.

## Логи

Основные места:

- `stdout`
- `logs/app.log`

В будущем для web можно добавить:

- `logs/web.log`

Формат:

- timestamp
- level
- logger name
- message

### Правила по логам

Логи должны быть:

- понятными;
- на английском языке;
- достаточными для диагностики текущей итерации;
- без утечки секретов.

Не добавляй:

- лишний debug noise без причины;
- сырые secret/env values;
- небезопасные dumps внешних payload;
- полный config dump без redaction;
- полный Jinja context dump.

## Artifacts / runtime files

`beeui` не является trading/runtime engine, поэтому он не должен создавать product runtime artifacts вроде `signals.jsonl`, `orders.jsonl`, `trades.jsonl`.

Допустимые локальные artifacts для самого `beeui`:

```text
logs/
storage/
```

Потенциальные future artifacts:

```text
storage/interfaces/config_changes/<change_id>/audit.json
storage/interfaces/config_revisions/<change_id>/settings.before.yml
storage/interfaces/operator_actions/<action_id>.json
```

Для demo/tests могут использоваться fixture artifacts:

```text
examples/demo_static/data/
tests/fixtures/
```

### Правила по artifacts

Artifacts должны быть:

- воспроизводимыми;
- объяснимыми;
- консистентными с логами;
- безопасными с точки зрения содержимого.

Не допускается:

- утечка секретов;
- запись в product storage без явного product callback;
- неочевидное изменение JSON/API contract без обновления docs;
- arbitrary filesystem browsing;
- hidden file write side effects в read-only routes.

## Интеграция с BeeCap и BeeAgent

### MVP integration mode: embedded

На этапе MVP `beeui` подключается как Python dependency внутрь продукта.

Пример структуры:

```text
beecap
  depends on beeui
  creates BeeCapUiAdapter
  calls create_beeui_app(...)
```

Пример будущего кода в BeeCap:

```python
from beeui_module.app import create_beeui_app
from beecap_module.interfaces.ui.adapter import BeeCapUiAdapter

app = create_beeui_app(
    product_id="beecap",
    product_title="BeeCap",
    adapter=BeeCapUiAdapter(...),
    config_path="config/beeui.yml",
)
```

### Локальная editable-интеграция

Во время разработки из соседней папки:

```bash
cd ~/Projects/beecap
uv pip install -e ../beeui
```

Или через `pyproject.toml` в `beecap`:

```toml
dependencies = [
    "beeui @ file:///home/bee/Projects/beeui",
]
```

Для временной локальной разработки допустимо. Для стабильного release лучше использовать Git tag или package registry.

### Future integration mode: standalone

Позже `beeui` сможет запускаться отдельным сервисом:

```text
beeui service
  → connects to beecap API
  → connects to beeagent API
```

Это не MVP.

Standalone mode требует:

- HTTP product adapter;
- auth/CORS/session policy;
- product service discovery;
- backend health/degraded states;
- deployment docs.

До стабилизации embedded mode standalone лучше не делать.

## Что должно остаться в Bee-продуктах

После внедрения `beeui` Bee-продукты не должны повторно реализовывать:

- Tabler templates;
- base layout;
- sidebar/navbar;
- generic cards;
- generic tables;
- generic artifact browser;
- theme layer;
- config UI shell;
- admin/support pages.

Bee-продукты должны реализовывать:

- product read-model;
- artifact allowlist;
- product-specific summaries;
- config validation callback;
- bounded action callbacks;
- authority/security-sensitive checks.

## Product adapter rule

`ProductUiAdapter` — единственная точка знания о конкретном продукте.

Generic BeeUI code не должен знать:

- что такое MRKT cycle;
- как считается Binance rollout;
- что такое BeeAgent capability;
- как устроен ROP classification;
- где именно продукт хранит внутренние domain artifacts.

Generic BeeUI code должен работать с нормализованными структурами:

- dashboard payload;
- run payload;
- artifact metadata;
- block data;
- config read-model;
- action definitions.

## Web UI rules

`beeui` web routes должны быть read-only by default.

Допустимые read-only routes:

- dashboard;
- pages;
- run views;
- artifact views;
- config read-model;
- admin/support summaries.

Write routes допустимы только если:

- они явно заявлены в текущей итерации;
- имеют validation;
- имеют CSRF/auth requirements, если auth включён;
- пишут audit artifact;
- не bypass-ят product authority boundary;
- вызывают только bounded product callback/API.

### HTML/Jinja rules

Обязательно:

- autoescape enabled;
- no raw untrusted HTML;
- no unsafe `|safe` без крайней причины;
- no secrets in template context;
- all user/product-provided text escaped;
- route params validated.

Нельзя:

- рендерить arbitrary HTML from config;
- принимать arbitrary JS snippets;
- строить filesystem path напрямую из URL;
- показывать full config без redaction.

## Static assets

Tabler assets должны обслуживаться контролируемо.

Предпочтительный MVP-вариант:

```text
src/beeui_module/static/vendor/tabler/
```

Допустимо временно использовать minimal local CSS для skeleton, но итоговая цель — локальный vendored/static Tabler bundle.

Не допускается:

- зависеть от CDN в production/internal deployment без явной причины;
- копировать demo-only tracking scripts;
- держать неиспользуемые heavy demo assets без cleanup.

## API rules

JSON API должен использовать стабильный envelope.

Минимальный envelope:

```json
{
  "status": "ok",
  "data": {},
  "warnings": [],
  "source": {}
}
```

Для ошибок:

```json
{
  "status": "error",
  "error": {
    "code": "invalid_input",
    "message": "Invalid run_id"
  },
  "warnings": []
}
```

Правила:

- no secrets in API;
- invalid input returns bounded error;
- missing product data returns `partial`, `empty` or `not_found`, а не stack trace;
- response shapes documented in `docs/API_CONTRACT.md`.

## SDLC-light workflow

В `beeui` используется упрощённый, но дисциплинированный процесс:

1. `ROADMAP` фиксирует итерацию
2. под итерацию создаётся `Issue`
3. работа идёт в отдельной ветке
4. изменения ограничиваются scope текущей итерации
5. определяется `change level`
6. выполняются tests, smoke-check, route/API/security checks
7. результат оформляется в `PR`
8. итерация считается закрытой после merge и выполнения DoD

### Роли артефактов процесса

#### ROADMAP

Отвечает на вопрос:

- куда идёт проект;
- что должно быть реализовано в итерации;
- какие checks / DoD обязательны.

#### Issue

Отвечает на вопрос:

- что именно нужно сделать;
- зачем это нужно;
- какой scope и deliverable у задачи;
- какой ожидается change level.

#### PR

Отвечает на вопрос:

- что реально сделано;
- как это проверено;
- какие тесты подтверждают готовность;
- какие quality/security checks были реально нужны и выполнены;
- какие limitations остались.

## Change levels

Для lightweight SDLC используются три уровня изменений.

### low-risk

Изменения без влияния на UI/API/security contract:

- docs;
- локальные tests;
- naming/comments;
- безопасные косметические template/style changes.

Обычно достаточно:

- `uv run pytest -q`;
- relevant smoke check;
- docs review.

### runtime-risk

Изменения, влияющие на behavior/contracts:

- config schema;
- page/block rendering;
- adapters;
- artifact parsing;
- API response shape;
- route behavior;
- config preview/apply;
- product integration.

Требуют:

- базовых checks;
- route/API tests;
- malformed input tests;
- partial/missing data tests;
- docs update if contract changed.

### security-sensitive

Изменения на trust boundary:

- auth/session/cookies;
- CSRF;
- file/path access;
- artifact browser;
- config apply/write;
- operator actions;
- secrets redaction;
- dependency surface;
- external product HTTP adapter;
- HTML/API exposure of untrusted payloads.

Требуют:

- усиленной проверки по `docs/SECURITY.md`;
- path traversal tests;
- secret leakage review;
- input validation tests;
- no arbitrary file access check;
- no unsafe HTML/JS injection check.

## Правило закрытия итерации

Итерацию закрываем через PR, а не только через issue comment.

### В Issue

Храним:

- постановку задачи;
- context;
- scope;
- deliverable;
- acceptance criteria;
- expected checks;
- notes.

### В PR

Храним:

- summary изменений;
- related issue;
- iteration / change level;
- tests;
- smoke checks;
- security notes;
- checklist;
- known limitations.

### В Issue comments

Можно дополнительно писать:

- промежуточные проверки;
- screenshots;
- route smoke notes;
- уточнения и наблюдения.

Но основное evidence для закрытия должно быть в PR.

## Definition of Done для изменения в коде

Изменение считается готовым, если:

- реализовано в рамках текущей итерации;
- запуск через ожидаемый entrypoint работает;
- `uv run pytest -q` проходит;
- HTML routes/API routes, если затронуты, покрыты тестами;
- malformed input handled safely;
- partial/missing product data handled explicitly;
- логи понятны;
- secrets не попадают в HTML/API/logs/artifacts;
- path traversal blocked where relevant;
- required checks из `docs/SDLC.md` и `docs/SECURITY.md` выполнены для данного типа изменения;
- docs обновлены, если менялся contract, behavior, routes, API или security boundary.

## Практика по веткам и коммитам

### Ветка

Делай отдельную ветку под задачу/итерацию.

Примеры:

- `feature/iter-0-project-skeleton`
- `feature/iter-1-tabler-shell`
- `feature/iter-5-product-adapter-contract`
- `fix/artifact-path-validation`
- `docs/update-dev-guide`

### Коммиты

Используй conventional commits.

Примеры:

- `feat(core): add beeui startup contract`
- `feat(web): add tabler shell v0`
- `feat(blocks): add metric card renderer`
- `fix(artifacts): reject unsafe artifact paths`
- `docs(dev-guide): add beeui development workflow`
- `test(config): add invalid page schema cases`

## Что проверять перед PR

Минимум:

```bash
uv run pytest -q
./start.sh doctor
git status
```

Если затронут web:

```bash
./start.sh serve --config config/demo.beeui.yml --host 127.0.0.1 --port 8780
```

Проверить:

- route smoke;
- logs;
- HTML output does not expose secrets;
- invalid inputs handled safely;
- ordinary launch did not mutate `uv.lock`.

### Типовой verification checklist

- config читается корректно;
- invalid config fails fast;
- routes работают;
- API envelope стабилен;
- missing/partial data handled explicitly;
- logs понятны;
- secrets не протекли;
- path traversal blocked;
- изменение не вышло за scope текущей итерации;
- required checks по change level выполнены.

## Как подключать BeeUI к BeeCap во время MVP

Практический порядок:

1. В `beeui` закрыть iterations 0–5.
2. В `beecap` добавить локальную dependency:

```toml
dependencies = [
    "beeui @ file:///home/bee/Projects/beeui",
]
```

3. В `beecap` добавить product adapter:

```text
src/beecap_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
```

4. В `beecap` добавить:

```text
config/beeui.yml
```

5. В `beecap` заменить/обернуть web app factory:

```python
from beeui_module.app import create_beeui_app
from beecap_module.interfaces.ui.adapter import BeeCapUiAdapter

app = create_beeui_app(
    product_id="beecap",
    product_title="BeeCap",
    adapter=BeeCapUiAdapter(...),
    config_path="config/beeui.yml",
)
```

6. Проверить:

```bash
cd ~/Projects/beecap
./start.sh web --no-open
uv run pytest -q
```

Правило:

> BeeCap должен отдавать read-model. BeeUI не должен угадывать BeeCap storage semantics напрямую.

## Как подключать BeeUI к BeeAgent

Порядок аналогичный:

1. Добавить dependency на `beeui`.
2. Добавить `BeeAgentUiAdapter`.
3. Добавить `config/beeui.yml`.
4. Подключить `create_beeui_app(...)` в web entrypoint.
5. Проверить routes/modules/artifacts/capabilities.

Минимальная структура в BeeAgent:

```text
src/beeagent_module/interfaces/ui/
  adapter.py
  read_model.py
  artifacts.py
  capabilities.py
  actions.py
```

Правило:

> BeeAgent capability/action authority остаётся в BeeAgent. BeeUI только отображает и вызывает bounded callbacks.

## Deployment guidance

### MVP deployment

На сервере сначала использовать embedded mode:

```text
container: beecap
  includes beeui as dependency
  exposes beecap web

container: beeagent
  includes beeui as dependency
  exposes beeagent web
```

Плюсы:

- проще;
- меньше инфраструктуры;
- нет CORS/service discovery;
- проще auth/session;
- быстрее MVP.

### Future deployment

После стабилизации API/contracts можно перейти к standalone mode:

```text
container: beeui
container: beecap-api
container: beeagent-api
```

Это требует отдельной итерации:

- HTTP product adapter;
- auth model;
- CORS policy;
- product registry;
- degraded backend handling;
- deployment docs.

Не делать standalone mode до MVP embedded integration.

## Как использовать AI / Copilot без лишней бюрократии

Правильный подход:

1. дать AI контекст текущей итерации;
2. ограничить scope;
3. заставить учитывать `ROADMAP`, `SDLC`, `SECURITY`;
4. требовать проверяемый результат: code + tests + smoke + PR summary.

Неправильный подход:

- просить “сделай как лучше” без итерации и scope;
- не указывать affected files;
- не требовать schema validation;
- не просить route/API/security checks;
- не просить указать change level и required checks.

## Copilot / AI prompt template (`beeui`)

```text
Нужно внести изменения в проект `beeui`.

### Контекст

- Проект: `beeui` (`Python 3.14+`, `uv`)
- Назначение: reusable Python/FastAPI/Jinja2/Tabler UI layer для Bee-продуктов
- Архитектура: маленькие итерации, declarative pages/blocks, product adapters, read-only by default
- SDLC-light: `ROADMAP → Issue → branch → code → tests → docs → PR → merge`
- Generic rule: BeeUI renders. Product decides.
- Основные process/security docs:
  - `docs/ROADMAP.md`
  - `docs/DEV_GUIDE.md`
  - `docs/SDLC.md`
  - `docs/SECURITY.md`

### Правила

- Сначала прочитай все перечисленные файлы, потом предлагай и вноси правки.
- Если по ходу нужен ещё файл — добавь его в список и тоже прочитай.
- Сначала соотнеси задачу с текущей итерацией из `docs/ROADMAP.md`; не выходи за её scope.
- Сначала определи `change level`:
  - `low-risk`
  - `runtime-risk`
  - `security-sensitive`
- Для выбранного `change level` определи required checks по `docs/SDLC.md` и `docs/SECURITY.md`.
- Делай только минимально необходимые изменения по KISS.
- Не рефактори вне задачи.
- Не протаскивай no-code builder, auth, config apply или standalone service раньше соответствующей итерации.
- Не добавляй product-specific domain logic в generic BeeUI renderers.

### Architecture rules

- BeeUI рендерит UI и API read-model.
- Product adapter является единственной точкой знания о BeeCap/BeeAgent domain semantics.
- Generic block renderers не должны знать, что такое MRKT, Binance, ROP, capability, strategy или broker.
- Read-only by default.
- Write/control actions допустимы только через bounded product callbacks/API, validation and audit.
- Не создавай второй source of truth.
- Не читай arbitrary filesystem paths из route params.
- Не используй unsafe HTML/Jinja `|safe` без необходимости.

### Config / source of truth rules

- UI source of truth: `beeui.yml`.
- Product source of truth остаётся в product config/artifacts/API.
- Если добавляется новый обязательный key в `beeui.yml`, он должен:
  - быть описан в docs/example config;
  - валидироваться fail-fast;
  - иметь tests на missing/invalid cases.
- Secrets не должны попадать в `beeui.yml`, HTML, API, logs or artifacts.

### Docs / contracts / API

Если меняется route/API/schema/block/config contract, проверь, нужно ли обновить:

- `docs/ROADMAP.md`
- `docs/DEV_GUIDE.md`
- `docs/SDLC.md`
- `docs/SECURITY.md`
- `docs/WEB_UI.md`
- `README.ru.md`

Если меняется JSON API, покажи пример response envelope.

Если меняется block schema, покажи пример YAML block config.

### Code style / execution rules

- Соблюдай PEP 8.
- Логи, имена полей, JSON/API/runtime messages — на английском языке.
- Комментарии на русском добавляй только там, где без них теряется смысл.
- Все команды запуска, тестов и smoke-check указывай через `uv run` или `./start.sh`.
- Не меняй `pyproject.toml.version`, если задача явно не про релиз.

### Формат ответа

Ответ строго в формате:

1. `Что прочитал`
2. `План`
3. `Change level`
4. `Required checks`
5. `Source of truth after change`
6. `Было`
7. `Стало`
8. `Почему`
9. `Чеклист`
10. `Что написать в PR`

### Дополнительно к формату

- Без diff.
- Без лишних рассуждений.
- Если нужна новая функция/класс — укажи точное место вставки.
- Для тестов перечисли, какие именно тесты нужно добавить/обновить.
- Для каждого нового или изменённого config/schema key укажи:
  - где он живёт;
  - почему именно там;
  - почему это не создаёт второй source of truth.
- Для PR кратко перечисли, что должно попасть в:
  - `Summary`
  - `Tests`
  - `Security review`
  - `Docs`
- Отдельно явно укажи: менялся ли `pyproject.toml.version`; если задача не про релиз, ответ должен быть `version not changed`.

### Задача

<опиши задачу одной фразой>

### Итерация

<укажи номер и название итерации из `docs/ROADMAP.md`>

### Issue context

<вставь кратко Summary / Scope / Deliverable / Acceptance Criteria из issue>

### Файлы

Обязательно прочитай:

- `docs/ROADMAP.md`
- `docs/DEV_GUIDE.md`
- `docs/SDLC.md`
- `docs/SECURITY.md`
- `README.ru.md`
- `pyproject.toml`
- `config/start.py`
- `src/beeui_module/app.py`
- `src/beeui_module/config.py`
- `src/beeui_module/settings.py`

Если нужно, добавь и прочитай также:

- `src/beeui_module/pages/models.py`
- `src/beeui_module/pages/router.py`
- `src/beeui_module/blocks/models.py`
- `src/beeui_module/blocks/registry.py`
- `src/beeui_module/adapters/base.py`
- `src/beeui_module/artifacts/safe_paths.py`
- `tests/test_smoke.py`
- `tests/test_config.py`
- `tests/test_app.py`

### Ожидаемый результат

- работает ожидаемый entrypoint
- `uv run pytest -q` проходит
- логи остаются понятными
- routes/API/schema работают по contract
- invalid input handled safely
- secrets не попадают в HTML/API/logs/artifacts
- required checks для данного `change level` определены и перечислены
- изменение готово к оформлению в PR по текущей итерации
```

## Мини-шаблон для issue-driven работы с AI

### Input

- Iteration: `<номер>`
- Goal: `<цель>`
- Scope: `<что включено / исключено>`
- Deliverable: `<что должно существовать>`
- Change level: `<low-risk | runtime-risk | security-sensitive>`
- Files: `<список файлов>`
- Checks: `<pytest / smoke / route / API / security checks>`
- DoD: `<критерии готовности>`

### Expected output

- точечный план изменений;
- change level и required checks;
- какие файлы менять;
- какие тесты обновить;
- какие routes/API проверить;
- что написать в PR.

## Чего не делать

Не делай так:

- не добавляй product-specific logic в generic BeeUI blocks;
- не читай arbitrary filesystem paths;
- не рендери arbitrary HTML/JS из config;
- не используй unsafe Jinja `|safe` без явной причины;
- не смешивай scope нескольких итераций в одном PR;
- не закрывай итерацию только словами “вроде работает”;
- не оставляй изменения без tests / smoke / route check;
- не допускай утечки секретов в HTML/API/logs/artifacts;
- не требуй все security-checks всегда, если они не нужны для данного change level;
- не усложняй решение сверх scope итерации;
- не делай standalone service до embedded MVP;
- не начинай no-code builder до стабилизации declarative schema.

## Быстрый рабочий сценарий

Типовой цикл для разработчика:

1. открыть `docs/ROADMAP.md`;
2. выбрать текущую итерацию;
3. открыть или создать issue;
4. определить `change level`;
5. создать ветку;
6. внести изменения;
7. прогнать:

```bash
./start.sh doctor
uv run pytest -q
```

8. если затронут web:

```bash
./start.sh serve --config config/demo.beeui.yml --host 127.0.0.1 --port 8780
```

9. проверить:

- `logs/app.log`;
- route/API behavior;
- secret leakage;
- `git status`;
- `uv.lock` не изменился от обычного запуска;

10. оформить PR;
11. приложить tests / route checks / checklist / security notes;
12. после review — merge.

## Полезное правило проекта

Если меняется хотя бы одно из этого:

- `beeui.yml` schema;
- route contract;
- API response envelope;
- block schema;
- adapter contract;
- artifact browser behavior;
- config preview/apply behavior;
- auth/session behavior;
- trust boundary / secrets / external input / file path access;

то проверь, нужно ли обновить:

- `docs/ROADMAP.md`
- `docs/DEV_GUIDE.md`
- `docs/SDLC.md`
- `docs/SECURITY.md`
- `docs/COMPONENTS.md`
- `docs/API_CONTRACT.md`
- `docs/WEB_UI.md`
- `docs/INTEGRATION.md`
- `README.ru.md`

## Резюме

`beeui` развивается маленькими, проверяемыми итерациями.

Ключевая дисциплина проекта:

- BeeUI renders, product decides;
- declarative UI schema;
- reusable blocks;
- product adapters;
- read-only by default;
- bounded write/actions only through product callbacks;
- no secrets in HTML/API/logs/artifacts;
- no arbitrary file access;
- change level-driven checks;
- PR-based iteration closure;
- embedded MVP first, standalone service later.
