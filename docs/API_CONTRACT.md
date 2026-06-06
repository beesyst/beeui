# API contract BeeUI

## Область действия

Iteration 12 определяет стабильный read-only envelope для adapter-backed
маршрутов product console:

- `GET /api/dashboard`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/venues/{venue_id}/dashboard`

Artifact API routes сохраняют существующий contract Iteration 11.

## Успешный ответ

```json
{
  "ok": true,
  "api": "beeui.v0",
  "read_only": true,
  "data": {},
  "warnings": [],
  "meta": {}
}
```

Для adapter result со статусом `partial` ответ остаётся успешным, а
`meta.status` получает значение `"partial"`.

## Ответ с ошибкой

```json
{
  "ok": false,
  "api": "beeui.v0",
  "read_only": true,
  "error": {
    "code": "adapter_unavailable",
    "message": "Adapter is not available"
  },
  "warnings": [],
  "meta": {}
}
```

Ожидаемое соответствие HTTP status:

- `invalid_id` → `400`
- `permission_denied` → `403`
- `not_found` → `404`
- `unavailable` / `adapter_unavailable` → `503`
- некорректные adapter results и неожиданные ошибки adapter → `502`

## Правила

- Product console API routes существуют только при передаче adapter во время
  создания приложения.
- Все маршруты используют только GET и содержат `read_only: true`.
- `run_id` и `venue_id` валидируются до вызова adapter.
- Исключения adapter нормализуются, внутренние детали исключений не раскрываются.
- Adapter payload считается недоверенным входом.
- Секреты не должны попадать в HTML или API responses.
- Route prefix и embedded mount сохраняют тот же envelope.
- Artifact API routes не переводятся на `beeui.v0` и сохраняют contract
  Iteration 11.
