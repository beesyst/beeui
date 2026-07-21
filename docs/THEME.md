# Theme

## Назначение

BeeUI поддерживает три режима темы:

- `system` — автоматический выбор на основе `prefers-color-scheme`;
- `light` — светлая тема;
- `dark` — тёмная тема.

Тема является только presentation preference. Она не влияет на product behavior, авторизацию или бизнес-логику.

## Механизм

### HTML-атрибут

Текущая тема устанавливается как `data-bs-theme` на корневом `<html>` элементе. Tabler и BeeUI CSS используют этот атрибут для переключения стилей.

### FOUC prevention

Для предотвращения Flash of Uncolored Theme используется inline `<script>` в `<head>`, который синхронно читает `localStorage` и устанавливает атрибут до первого рендеринга страницы:

```javascript
var d=document.documentElement,c=d.getAttribute('data-beeui-theme-config'),s=window.localStorage.getItem('beeui-theme');
if(s!=='system'&&s!=='light'&&s!=='dark'){if(s)window.localStorage.removeItem('beeui-theme');s=null}
var m=s||((c==='system'||c==='light'||c==='dark')?c:'system');
d.setAttribute('data-bs-theme',m==='system'&&window.matchMedia('(prefers-color-scheme:dark)').matches?'dark':m==='system'?'light':m);
```

Правила:

- Только canonical allowlisted значения (`system`, `light`, `dark`) принимаются из `localStorage`.
- Если сохранённого выбора нет, применяется configured mode; `prefers-color-scheme` используется только для effective `system`.
- Invalid stored value удаляется и ignored.
- FOUC bootstrap не принимает произвольный JS/data.

### Переключение темы

Кнопки переключения темы (`system`, `light`, `dark`) сохраняют explicit canonical choice в `localStorage` и изменяют `data-bs-theme` на effective `light` или `dark`.

### Синхронизация графиков

При загрузке страницы тема графиков ApexCharts синхронизируется с текущей `data-bs-theme`:

```javascript
var themeMode = html.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
config.theme = config.theme || {};
config.theme.mode = themeMode;
```

При переключении темы все зарегистрированные графики обновляются через `chart.updateOptions()`.

## Конфигурация

Начальная тема в demo mode задаётся через `config/schema.yml`:

```yaml
app:
  theme:
    mode: dark
```

Поддерживаемые значения `mode`:

- `light`
- `dark`
- `system`

Compatibility alias `auto` принимается только при загрузке существующей config и нормализуется к `system`.

Invalid mode в config приводит к fail-fast при загрузке.

## Границы безопасности

- `localStorage` не влияет на product behavior или authorization.
- Browser state не является вторым product/config source of truth.
- Тема — только presentation preference.
- Session cookie и auth decisions не зависят от `data-bs-theme`.
- Нет external scripts, CDN или tracking для theme.
