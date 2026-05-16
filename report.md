# M2

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

# M3

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
Основной файл [server.py](mcp-proshop-features/server.py)
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


## Часть 2 — RAG 

Отчет о задании.

### Стек
* Векторная БД  postgres + pgvector
* Модель для embedding/search - локальная ollama bge-m3

### Chunking
* **Script** `M3-rag/chunker/chunker.py`
* **Files processed:** 47
* **Total chunks:** 457
* **Output:** `M3-rag/chunks.jsonl`

Chunks by doc_type

| doc_type | count |
|----------|-------|
| `adr` | 17 |
| `api_endpoint` | 69 |
| `feature` | 60 |
| `generic` | 179 |
| `glossary` | 41 |
| `incident` | 11 |
| `page` | 15 |
| `runbook` | 65 |

### Embedding

**Script** `M3-rag/embedder.py`

**Output:** postgres with pgvector extension

### Search
* **Script** `M3-rag/embedder.py`

#### Пример 1

```shell
python3 query.py "Какая платежная система используется " 3

  [1] score=0.5993
       source: checkout.md
       type:   feature
       heading: Feature 3: Payment Method Selection
       text:  ## Feature 3: Payment Method Selection

### Назначение
Второй шаг checkout — выбор способа оплаты (PayPal или Credit Card через PayPal). Выбор сохраняется в Redux и localStorage. Persona: покупатель перед оплатой.

### User flow
1. После заполнения а... [truncated]

  [2] score=0.5915
       source: adr-004-paypal-vs-stripe.md
       type:   adr
       heading: ADR-004: Use PayPal as the Payment Processor
       text:  # ADR-004: Use PayPal as the Payment Processor

**Status:** Accepted (for current deployment); Superseded by preference for Stripe on new projects
**Date:** 2023-04-20
**Decision Makers:** Engineering team

---

## Context

The ProShop application ne... [truncated]

  [3] score=0.5803
       source: adr-004-paypal-vs-stripe.md
       type:   adr
       heading: ADR-004: Use PayPal as the Payment Processor
       text:  ---

## Alternatives Considered

### Stripe

Stripe is now the team's preferred payment processor for new projects. Key advantages over PayPal:

- **Test mode is a faithful replica of production.** Stripe test mode uses the same code paths as product... [truncated]

```

#### Пример 2

```shell
python3 query.py "Какая БД используется в proshop mern " 3

[1] score=0.6236
source: feature-flags-spec.md
type:   generic
heading: Feature Flags in This Project
text:  ### Feature Flags in This Project

The ProShop MERN codebase is a teaching project: a full-stack e-commerce application built with MongoDB, Express, React, and Node.js. It contains a product catalog, shopping cart, multi-step checkout, PayPal payment... [truncated]

[2] score=0.6212
source: architecture.md
type:   generic
heading: 1. System Overview
text:  ## 1. System Overview

ProShop is a full-stack e-commerce web application built with the MERN stack
(MongoDB, Express, React, Node). It ships a working storefront where customers
browse a product catalogue, build a cart, authenticate, complete a mult... [truncated]

[3] score=0.6075
source: best-practices.md
type:   generic
heading: 1. Introduction: Why proshop_mern Is Deprecated
text:  ## 1. Introduction: Why proshop_mern Is Deprecated

The original `proshop_mern` fork (bradtraversy/proshop_mern) was built circa 2020–2022 with:

- **React 17** — predates concurrent rendering and Server Components
- **Create React App** — unmaintain... [truncated]
```

## Часть 3 - Search-docs MCP

* **Script** `mcp-search-docs/mcp_server.py` — FastMCP-сервер с одним инструментом: `search_project_docs(query, top_k=5)`
* Семантический поиск по документации через pgvector + Ollama bge-m3 (переиспользует `query.py`)
* Возвращает `List[Chunk]` с полями: `source_file`, `file_path`, `title`, `parent_headings` (breadcrumbs), `score`, `snippet` (~200 символов)
* Описание инструмента по принципам MCP design: когда вызывать (поиск по продукту proshop_mern) и когда НЕ вызывать (feature-flags MCP)
* Транспорт: stdio (по умолчанию для MCP-клиентов)

Дата прогона: 2026-05-16

### Вопрос 1: Какая БД используется и почему?

**Запрос:** `search_project_docs("What database is used and why", top_k=5)` → доуточнен запросом `search_project_docs("ADR-001 MongoDB Mongoose primary database decision rationale", top_k=5)`

#### Чанки MCP (запрос 1 — initial)

| # | id | score | source_file | snippet (фрагмент) |
|---|----|-------|-------------|-------------------|
| 1 | adr-001-mongodb-vs-postgres.md | 0.5757 | `docs/project-data/adrs/adr-001-mongodb-vs-postgres.md` | `# ADR-001: Use MongoDB (via Mongoose) as the Primary Database **Status:** Accepted **Date:** 2023-01-10` |
| 2 | local-setup.md | 0.5471 | `docs/project-data/runbooks/local-setup.md` | `This script (backend/seeder.js) populates the database with sample users, products, and empty orders.` |
| 3 | dev-history.md | 0.5315 | `docs/project-data/dev-history.md` | `### Decision 1: MongoDB over PostgreSQL Made in January 2023 before the first commit. The rationale: the product catalog has variable attributes` |
| 4 | best-practices.md | 0.5278 | `docs/project-data/best-practices.md` | `### 9.2 Permissions in the database, not the codebase Hard-coded role checks` |
| 5 | db-seed-and-reset.md | 0.5218 | `docs/project-data/runbooks/db-seed-and-reset.md` | `## Overview ### Seed Operations Available` |

#### Чанки MCP (запрос 1 — уточняющий)

| # | id | score | source_file | snippet (фрагмент) |
|---|----|-------|-------------|-------------------|
| 1 | adr-001-mongodb-vs-postgres.md | 0.6738 | `docs/project-data/adrs/adr-001-mongodb-vs-postgres.md` | Полный текст ADR: MongoDB via Mongoose, решение от 2023-01-10 |
| 2 | best-practices.md | 0.5866 | `docs/project-data/best-practices.md` | `## 3. Mongoose Schema Design Best Practices` |
| 3 | adr-001-mongodb-vs-postgres.md | 0.5783 | `docs/project-data/adrs/adr-001-mongodb-vs-postgres.md` | `The Order document embeds order items... reflecting MongoDB's document-oriented modeling` |
| 4 | dev-history.md | 0.5707 | `docs/project-data/dev-history.md` | `### Decision 1: MongoDB over PostgreSQL Made in January 2023 before the first commit` |
| 5 | best-practices.md | 0.5656 | `docs/project-data/best-practices.md` | `### Mongoose / Database - [ ] **Add compound indexes**` |

**Ответ:** Используется **MongoDB** через ODM **Mongoose** (ADR-001: статус Accepted, дата 2023-01-10). Причины:
- **Schema flexibility** для товаров с переменными атрибутами (электроника, одежда, книги) — добавление полей без миграций.
- **Embedded documents** для order items — атомарный fetch заказа, сохранение исторических цен.
- **Mongoose ODM** — beginner-friendly, быстрая адаптация команды.
- **MongoDB Atlas free tier** (M0) — нулевая инфраструктурная стоимость на 6 месяцев.
- **Aggregation pipeline** для расчёта average rating / review count.

Альтернативы: PostgreSQL (отказан — команда хотела опыт MongoDB), SQLite (отказан — не для production multi-connection). В Assessment (апрель 2026) признано, что PostgreSQL + JSONB был бы не хуже, но цена миграции превышает benefit.

---

### Вопрос 2: Какие фичи зависят от search_v2?

**Запрос:** `search_project_docs("search_v2 dependencies what features depend on search_v2", top_k=5)` → уточнение `search_project_docs("search_v2 dependencies field requires depends_on", top_k=5)`

#### Чанки MCP (запрос 2 — initial)

| # | id | score | source_file | snippet (фрагмент) |
|---|----|-------|-------------|-------------------|
| 1 | feature-flags-spec.md | 0.6419 | `docs/project-data/feature-flags-spec.md` | `### Search & Discovery #### search_v2 — New Search Algorithm **Default state:** Testing (15%)` |
| 2 | feature-flags-spec.md | 0.5579 | `docs/project-data/feature-flags-spec.md` | `### Example Feature Object "search_v2": { "name": "New Search Algorithm" ` |
| 3 | catalog.md | 0.5196 | `docs/project-data/features/catalog.md` | `## Feature 2: Product Search Полнотекстовый поиск по названию товара через URL-параметр` |
| 4 | feature-flag-toggle.md | 0.5078 | `docs/project-data/runbooks/feature-flag-toggle.md` | `Feature flags are stored in MongoDB and checked at runtime.` |
| 5 | features-analysis-ru.md | 0.5053 | `docs/project-data/features-analysis-ru.md` | `multi_step_checkout_v2. Это та фича, которую студенты обязаны сохранить` |

#### Чанки MCP (запрос 2 — уточняющий)

| # | id | score | source_file | snippet (фрагмент) |
|---|----|-------|-------------|-------------------|
| 1 | feature-flags-spec.md | 0.5884 | `docs/project-data/feature-flags-spec.md` | `### Search & Discovery #### search_v2 — New Search Algorithm **Dependencies:** None. This is a prerequisite for semantic_search.` |
| 2 | uploads.md | 0.5543 | `docs/project-data/api/uploads.md` | `## File Requirements` |
| 3 | feature-flags-spec.md | 0.5397 | `docs/project-data/feature-flags-spec.md` | `### Example Feature Object "search_v2": {...` |
| 4 | admin.md | 0.5385 | `docs/project-data/features/admin.md` | `### Зависимости - Зависит от: multer...` |
| 5 | feature-flags-spec.md | 0.5366 | `docs/project-data/feature-flags-spec.md` | `### Tool 2: set_feature_state **Purpose:** Change the status` |

**Ответ:** От `search_v2` зависит **одна фича**:
- **`semantic_search`** (Semantic Vector Search) — в feature-flags-spec.md чётко указано: «`search_v2` must be `"Enabled"` first». В features.json подтверждено: `"dependencies": ["search_v2"]`.

Sam `search_v2` не имеет никаких зависимостей («Dependencies: None»).

---

### Вопрос 3: Что случилось во время последнего incident с checkout?

**Запрос:** `search_project_docs("last incident checkout", top_k=5)` → уточнения `search_project_docs("checkout incident outage failure postmortem", top_k=5)` и `search_project_docs("checkout incident PayPal outage timeline root cause impact", top_k=5)`

#### Чанки MCP (запрос 3 — initial)

| # | id | score | source_file | snippet (фрагмент) |
|---|----|-------|-------------|-------------------|
| 1 | feature-flags-spec.md | 0.5971 | `docs/project-data/feature-flags-spec.md` | `### Checkout #### express_checkout — Express One-Click Checkout` |
| 2 | incident-response.md | 0.5968 | `docs/project-data/runbooks/incident-response.md` | `## Phase 6: Communication ### Timeline` |
| 3 | incident-response.md | 0.5940 | `docs/project-data/runbooks/incident-response.md` | `## Incident Postmortem: PayPal Payment Processor Outage **Date:** 2024-04-15` |
| 4 | checkout.md | 0.5567 | `docs/project-data/features/checkout.md` | `### Назначение Финальный шаг checkout — полный обзор заказа` |
| 5 | incident-response.md | 0.5529 | `docs/project-data/runbooks/incident-response.md` | `## Phase 1: Discovery & Declaration (0–5 Minutes)` |

#### Чанки MCP (запрос 3 — уточняющий 1)

| # | id | score | source_file | snippet (фрагмент) |
|---|----|-------|-------------|-------------------|
| 1 | incident-response.md | 0.6419 | `docs/project-data/runbooks/incident-response.md` | `## Incident Postmortem: PayPal Payment Processor Outage **Date:** 2024-04-15 **Duration:** 10 minutes (14:22–14:32 UTC)` |
| 2 | i-001-paypal-double-charge.md | 0.6718 | `docs/project-data/incidents/i-001-paypal-double-charge.md` | `# Incident i-001: PayPal Sandbox Webhook Double-Charge **Severity:** P1` |
| 3 | incident-response.md | 0.6694 | `docs/project-data/runbooks/incident-response.md` | `## Phase 6: Communication ### Timeline` |
| 4 | incident-response.md | 0.6508 | `docs/project-data/runbooks/incident-response.md` | `## Phase 1: Discovery & Declaration` |
| 5 | adr-004-paypal-vs-stripe.md | 0.6301 | `docs/project-data/adrs/adr-004-paypal-vs-stripe.md` | `ADR-004: Use PayPal as the Payment Processor` |

#### Чанки MCP (запрос 3 — уточняющий 2)

| # | id | score | source_file | snippet (фрагмент) |
|---|----|-------|-------------|-------------------|
| 1 | incident-response.md | 0.7270 | `docs/project-data/runbooks/incident-response.md` | `## Incident Postmortem: PayPal Payment Processor Outage **Date:** 2024-04-15 **Duration:** 10 minutes` |
| 2 | i-001-paypal-double-charge.md | 0.6718 | `docs/project-data/incidents/i-001-paypal-double-charge.md` | `# Incident i-001: PayPal Sandbox Webhook Double-Charge **Severity:** P1` |
| 3 | incident-response.md | 0.6694 | `docs/project-data/runbooks/incident-response.md` | `## Phase 6: Communication ### Timeline` |
| 4 | incident-response.md | 0.6508 | `docs/project-data/runbooks/incident-response.md` | `## Phase 1: Discovery & Declaration` |
| 5 | adr-004-paypal-vs-stripe.md | 0.6301 | `docs/project-data/adrs/adr-004-paypal-vs-stripe.md` | `ADR-004: Use PayPal as the Payment Processor` |

**Ответ:** Последний incident, затрагивающий checkout, описан в `incident-response.md` как **«PayPal Payment Processor Outage»** (INC-2024-042):

- **Дата:** 2024-04-15, **длительность:** 10 мин (14:22–14:32 UTC), **Severity:** P1.
- **Timeline:** 14:20 — мониторинг обнаружил 401 от Payment API; 14:22 — репорт «Can't checkout»; 14:24 — IC объявил incident; 14:26 — root cause identified: PayPal credentials expired; 14:28 — credentials renewed & redeployed; 14:32 — all-clear.
- **Root cause:** PayPal API credentials имели 1-годичный срок (до 2024-04-15) и не было ни напоминания, ни мониторинга истечения.
- **Impact:** ~150 заказов задержаны, 10 мин checkout failures, ~5 жалоб в соцсетях. Потерь выручки нет — заказы повторены.
- **Remediation:** Calendar reminder, automated credential expiry monitoring, Datadog/Sentry alert на 401, credential rotation checklist.

Дополнительно найден более ранний checkout-related incident **i-001** (2023-11-04): PayPal Sandbox Webhook Double-Charge — `onApprove` callback сработал дважды, из-за отсутствия idempotency check на `PUT /api/orders/:id/pay` 7 заказов получили дубликаты paymentResult, 3 товара — двойной декремент stock (один до -1). Фикс: guard `if (order.isPaid) return` + защита в middleware.


