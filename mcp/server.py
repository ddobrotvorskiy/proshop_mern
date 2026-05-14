#!/usr/bin/env python3
"""
ProShop Feature Flags MCP Server.

Exposes three tools for managing feature flags via the ProShop API:
- get_feature_info: Retrieve feature state
- set_feature_state: Change feature status (Disabled/Testing/Enabled)
- adjust_traffic_rollout: Modify traffic percentage for Testing features

Transport: stdio (for use with Claude Desktop or MCP CLI)
"""

import asyncio
import httpx
import anyio
from fastmcp import FastMCP

from config import Config
from auth import AuthManager
from client import ProShopClient


# Initialize FastMCP server
mcp = FastMCP("proshop-feature-flags")

# Global client instance
_client: ProShopClient | None = None


async def _get_client() -> ProShopClient:
    """Get or initialize the API client."""
    global _client
    if _client is None:
        raise RuntimeError("Client not initialized. Server startup failed.")
    return _client


@mcp.tool()
async def get_feature_info(feature_id: str) -> dict:
    """
    Получить полное текущее состояние одного фича-флага.

    Возвращает все поля записи: name, description, status, traffic_percentage,
    last_modified, targeted_segments, rollout_strategy, dependencies.

    КОГДА ВЫЗЫВАТЬ:
    - Перед любым изменением флага — убедиться в его текущем состоянии.
    - Когда пользователь спрашивает о статусе, проценте трафика или зависимостях конкретной фичи.
    - Для проверки, что предыдущая операция записи применилась корректно.
    - При диагностике: выяснить, почему фича не работает или ведёт себя неожиданно.

    КОГДА НЕ ВЫЗЫВАТЬ:
    - Если нужно получить список всех флагов сразу — этот инструмент возвращает только один флаг.
    - Если feature_id уже известен и актуален из предыдущего ответа в том же диалоге —
      повторный вызов только тратит время.
    - Для изменения состояния флага — используй set_feature_state или adjust_traffic_rollout.

    Args:
        feature_id: Ключ фичи в snake_case (например, "search_v2", "dark_mode").

    Returns:
        Объект фичи со всеми полями, либо объект ошибки:
        - FEATURE_NOT_FOUND — feature_id не существует в features.json.
        - FILE_READ_ERROR — файл features.json недоступен.
        - JSON_PARSE_ERROR — файл содержит невалидный JSON.

    Example:
        >>> await get_feature_info("dark_mode")
        {
            "feature_id": "dark_mode",
            "name": "Dark Mode Theme",
            "status": "Testing",
            "traffic_percentage": 20,
            "last_modified": "2026-04-20",
            ...
        }
    """
    client = await _get_client()
    return await client.get_feature(feature_id)


@mcp.tool()
async def set_feature_state(feature_id: str, state: str) -> dict:
    """
    Изменить статус фича-флага: Disabled, Testing или Enabled.

    Автоматически корректирует traffic_percentage под новый статус:
    - Disabled  → traffic_percentage становится 0.
    - Testing   → traffic_percentage остаётся, если уже в диапазоне 1–99; иначе сбрасывается на 10.
    - Enabled   → traffic_percentage становится 100.

    Всегда обновляет поле last_modified на сегодняшнюю дату.
    При переходе в Testing или Enabled проверяет зависимости:
    если зависимая фича не Enabled — в ответе появится массив warnings (не блокирует операцию).

    КОГДА ВЫЗЫВАТЬ:
    - Чтобы запустить фичу в тестовый режим: set_feature_state(id, "Testing").
    - Чтобы полностью включить фичу для всего трафика: set_feature_state(id, "Enabled").
    - Чтобы экстренно отключить фичу (kill switch): set_feature_state(id, "Disabled").
    - Чтобы завершить A/B-тест — включить победителя и выключить проигравшего.
    - Чтобы перевести флаг из Testing в Enabled после успешного canary-роллаута на 100%.

    КОГДА НЕ ВЫЗЫВАТЬ:
    - Если нужно только изменить процент трафика у фичи, уже находящейся в Testing —
      используй adjust_traffic_rollout (он не трогает статус).
    - Если текущий статус уже совпадает с целевым — лишний вызов перезапишет last_modified.
    - Для чтения состояния флага — используй get_feature_info.

    Args:
        feature_id: Ключ фичи в snake_case (например, "stripe_alternative").
        state: Целевой статус — строго одно из: "Disabled", "Testing", "Enabled" (с учётом регистра).

    Returns:
        Обновлённый объект фичи с полем warnings (может быть пустым массивом),
        либо объект ошибки:
        - FEATURE_NOT_FOUND — feature_id не существует.
        - INVALID_STATE — state не входит в список допустимых значений.
        - FILE_READ_ERROR / FILE_WRITE_ERROR — проблема с чтением или записью features.json.

    Example:
        >>> await set_feature_state("dark_mode", "Enabled")
        {
            "feature_id": "dark_mode",
            "status": "Enabled",
            "traffic_percentage": 100,
            "last_modified": "2026-05-14",
            ...
        }
    """
    # Validate state before making API call
    valid_states = {"Disabled", "Testing", "Enabled"}
    if state not in valid_states:
        return {
            "error": "INVALID_STATE",
            "message": f"State '{state}' is not valid. Must be one of: Disabled, Testing, Enabled (case-sensitive).",
            "feature_id": feature_id,
        }
    
    client = await _get_client()
    return await client.set_feature_state(feature_id, state)


@mcp.tool()
async def adjust_traffic_rollout(feature_id: str, percentage: int) -> dict:
    """
    Изменить процент трафика для фичи, находящейся в статусе Testing.

    Не меняет статус флага. Работает только если status == "Testing".
    Обновляет last_modified на сегодняшнюю дату.

    Подсказки в ответе (поле hint):
    - percentage == 0   → подсказка использовать set_feature_state("Disabled") вместо этого.
    - percentage == 100 → подсказка повысить статус до Enabled через set_feature_state.

    КОГДА ВЫЗЫВАТЬ:
    - При canary-роллауте: пошагово увеличивать трафик (5% → 25% → 50% → 100%)
      между периодами наблюдения за метриками.
    - При A/B-тесте: выставить 50% для равномерного разделения трафика.
    - Чтобы снизить трафик при первых признаках деградации, не отключая флаг полностью.
    - Чтобы расширить тест после подтверждения стабильности на предыдущем пороге.

    КОГДА НЕ ВЫЗЫВАТЬ:
    - Если фича не в статусе Testing — вызов вернёт ошибку WRONG_STATUS_FOR_ROLLOUT.
      Сначала переведи флаг в Testing через set_feature_state.
    - Если нужно полностью включить или выключить фичу — используй set_feature_state:
      он корректно меняет статус и трафик одновременно.
    - Для чтения текущего процента трафика без изменений — используй get_feature_info.

    Args:
        feature_id: Ключ фичи в snake_case (например, "search_v2").
        percentage: Целевой процент трафика — целое число от 0 до 100 включительно.

    Returns:
        Обновлённый объект фичи с полем hint (или null),
        либо объект ошибки:
        - FEATURE_NOT_FOUND — feature_id не существует.
        - WRONG_STATUS_FOR_ROLLOUT — фича не в статусе Testing.
        - INVALID_PERCENTAGE — percentage не является целым числом или выходит за пределы 0–100.
        - FILE_READ_ERROR / FILE_WRITE_ERROR — проблема с чтением или записью features.json.

    Example:
        >>> await adjust_traffic_rollout("search_v2", 50)
        {
            "feature_id": "search_v2",
            "status": "Testing",
            "traffic_percentage": 50,
            "last_modified": "2026-05-14",
            "hint": null
        }
    """
    # Validate percentage before making API call
    if not isinstance(percentage, int) or percentage < 0 or percentage > 100:
        return {
            "error": "INVALID_PERCENTAGE",
            "message": f"percentage must be an integer from 0 to 100, got {percentage}",
            "feature_id": feature_id,
        }
    
    client = await _get_client()
    return await client.adjust_traffic_rollout(feature_id, percentage)


async def _initialize_and_run() -> None:
    """Initialize client and run MCP server."""
    global _client
    
    config = Config.from_env()
    
    async with httpx.AsyncClient() as http_client:
        await AuthManager.initialize(config, http_client)
        _client = ProShopClient(config, http_client)
        
        # Run MCP server using anyio to avoid event loop conflicts
        def sync_run():
            mcp.run()
        
        await anyio.to_thread.run_sync(sync_run)


def main() -> None:
    """Initialize server and start listening."""
    try:
        anyio.run(_initialize_and_run)
    except RuntimeError as e:
        print(f"Startup failed: {e}", flush=True)
        raise
    except KeyboardInterrupt:
        print("Shutting down...", flush=True)


if __name__ == "__main__":
    main()
