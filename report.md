# M2 — Report

## IDE
- Primary (с ней я работал основной): OpenCode → rules в `AGENTS.md`

## Шаг 1 - Rules diff (что добавил руками поверх auto-generated)
- Добавлен файл `openapi-external.yaml` - из AGENTS.md удалено перечисление API методов 
- Удалено подробное перечисление моделей - с ростом сложности проекта одних моделей может стать слишком много для постоянной загрузки в контекст
- Удалено упоминание Heroku, так как деплой туда не будет производиться

## Документировать запуск в README
- запустил локально через docker mongo + npm run dev
- обновил описание README.md
- описал проблему с занятым 5000 портом на macos

### FINDINGS — что не так с проектом
- FINDINGS.orig.md - сгенерирован с помощью sonnet
- FINDINGS.md - оформлен ТОП 10 с помощью haiku
- Исправлен FINDINGS #1 с помощью haiku.

### NH-1 - архитектурная диаграмма
- docs/architecture.md - сгенерирован haiku

### NH-2 - ADR
- docs/adr/000*.md - сгенерированы sonnet

### NH-3 - Characterization tests на 1 функцию
- функция расчета цены `calculatePrices` выделена в отдельный файл [priceCalculator.js](frontend%2Fsrc%2Futils%2FpriceCalculator.js)
- сгенерирован Jest тест, фиксирующий текущее поведение
- выполнен рефакторинг функции с сохранением поведения

## 3 вопроса
- Сколько заняло бы вручную: 2 дня 
- Самая магическая функция IDE: пока что все это воспринимается как магия
- Где AI сломал и как пофиксил: AI указал неверный URL на коммит. Использовал URL проекта anomaly/opencode. Исправлено руками.

# M3 — Report

## Часть 1 — Feature Flags MCP server

### Feature-Flags API & Page

Реализован API и страница для управления фича-флагами.
- API http://localhost:3000/api/features
- Страница http://localhost:3000/admin/feature-flags

Состояние флагов хранится в json-файле ./backend/feature.json
Файл перезаписывается при изменениях.

### MCP-сервер

Реализован MCP сервер для управления feature-флагами Proshop MERN
Код MCP сервера на python, FastMCP
Основной файл [server.py](mcp/server.py)
Добавлен Bash скрипт для подключения env-переменных из ./mcp/.env, а не настроек opencode, так как там секреты.

Пример подключения для opencode. project-level `opencode.json`
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "proshop-features": {
      "type": "local",
      "command": ["/Users/dobrotvorskiy/repo/AI/proshop_mern/mcp/run_server.sh"],
      "enabled": true
    }
  }
}
```

### Feature flags MCP — полный лог
Полный текст сессии [m3-part1-mcp-session-log.md](sessions%2Fm3-part1-mcp-session-log.md)

**Дата прогона:** 2026-05-15

#### Шаг 1 — get_feature_info

**Tool call:** `get_feature_info(feature_id="search_v2")`

**Ответ MCP:**
```json
{
  "feature_id": "search_v2",
  "name": "New Search Algorithm",
  "description": "Replaces legacy regex-based keyword matching with a hybrid BM25 + TF-IDF ranking pipeline. Improves relevance for multi-word queries and handles common misspellings via fuzzy matching. Backend: new productController search path; index built on name, brand, category, description fields.",
  "status": "Disabled",
  "traffic_percentage": 0,
  "last_modified": "2026-05-15",
  "targeted_segments": ["beta_users", "internal"],
  "rollout_strategy": "canary"
}
```

**Вывод:** статус `Disabled` — необходимо перевести в `Testing`.

#### Шаг 2 — set_feature_state

**Tool call:** `set_feature_state(feature_id="search_v2", state="Testing")`

**Ответ MCP:**
```json
{
  "feature_id": "search_v2",
  "name": "New Search Algorithm",
  "status": "Testing",
  "traffic_percentage": 10,
  "last_modified": "2026-05-15",
  "targeted_segments": ["beta_users", "internal"],
  "rollout_strategy": "canary"
}
```

**Вывод:** статус изменён на `Testing`, трафик автоматически выставлен на 10% (дефолт для Testing).

#### Шаг 3 — adjust_traffic_rollout

**Tool call:** `adjust_traffic_rollout(feature_id="search_v2", percentage=25)`

**Ответ MCP:**
```json
{
  "feature_id": "search_v2",
  "name": "New Search Algorithm",
  "status": "Testing",
  "traffic_percentage": 25,
  "last_modified": "2026-05-15",
  "targeted_segments": ["beta_users", "internal"],
  "rollout_strategy": "canary"
}
```

**Вывод:** трафик выставлен на 25%.

#### Шаг 4 — get_feature_info (подтверждение)

**Tool call:** `get_feature_info(feature_id="search_v2")`

**Ответ MCP:**
```json
{
  "feature_id": "search_v2",
  "name": "New Search Algorithm",
  "description": "Replaces legacy regex-based keyword matching with a hybrid BM25 + TF-IDF ranking pipeline. Improves relevance for multi-word queries and handles common misspellings via fuzzy matching. Backend: new productController search path; index built on name, brand, category, description fields.",
  "status": "Testing",
  "traffic_percentage": 25,
  "last_modified": "2026-05-15",
  "targeted_segments": ["beta_users", "internal"],
  "rollout_strategy": "canary"
}
```

#### Итоговое состояние фичи search_v2

| Поле               | Значение                  |
|--------------------|---------------------------|
| feature_id         | search_v2                 |
| name               | New Search Algorithm      |
| status             | Testing                   |
| traffic_percentage | 25                        |
| rollout_strategy   | canary                    |
| targeted_segments  | beta_users, internal      |
| last_modified      | 2026-05-15                |
