# ProShop Feature Flags MCP Server

An MCP (Model Context Protocol) server for managing feature flags in the ProShop MERN e-commerce application. Allows AI assistants to query and modify feature flags via HTTP API in real time.

## Architecture

```
mcp/
├── server.py              # FastMCP app & three tools
├── client.py              # HTTP client wrapper for ProShop API
├── auth.py                # JWT authentication & token caching
├── config.py              # Configuration from environment
├── requirements.txt       # Python dependencies
├── tests/                 # Unit tests with pytest
├── venv/                  # Python virtual environment
└── README.md              # This file
```

## Features

Three MCP tools for managing feature flags:

1. **`get_feature_info`** — Retrieve complete state of a single feature flag
2. **`set_feature_state`** — Change feature status (Disabled → Testing → Enabled)
3. **`adjust_traffic_rollout`** — Modify traffic percentage for Testing features

All tools communicate with ProShop's feature flags API endpoints:
- `GET /api/features/:featureId`
- `PATCH /api/features/:featureId/state`
- `PATCH /api/features/:featureId/traffic`

## Setup

### Requirements

- Python 3.11+
- ProShop backend running on `http://localhost:5000`
- Admin credentials for authentication

### Installation

1. **Create virtual environment:**
   ```bash
   cd mcp-proshop-features
   python3.11 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the `mcp/` directory or set environment variables:

```bash
PROSHOP_API_URL="http://localhost:5000"
PROSHOP_ADMIN_EMAIL="admin@example.com"
PROSHOP_ADMIN_PASSWORD="your_password_here"
```

**Environment Variables:**

| Variable | Required | Default | Description |
|---|---|---|---|
| `PROSHOP_API_URL` | No | `http://localhost:5000` | Base URL of ProShop backend |
| `PROSHOP_ADMIN_EMAIL` | **Yes** | — | Admin email for login |
| `PROSHOP_ADMIN_PASSWORD` | **Yes** | — | Admin password for login |

## Usage

### Running the Server

```bash
cd mcp
./run_server.sh
```

The server will:
1. Load configuration from environment variables
2. Authenticate with ProShop backend (fail fast if credentials are invalid)
3. Start listening on stdio transport

### Claude Desktop Integration

Add this to Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "proshop-features": {
      "command": "python3",
      "args": ["/absolute/path/to/proshop_mern/mcp/server.py"],
      "env": {
        "PROSHOP_API_URL": "http://localhost:5000",
        "PROSHOP_ADMIN_EMAIL": "admin@example.com",
        "PROSHOP_ADMIN_PASSWORD": "your_password"
      }
    }
  }
}
```

### OpenCode Integration

Add this to OpenCode's `opencode.json`:

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

### API Contract

#### Tool 1: `get_feature_info`

**Parameters:**
- `feature_id` (string): Snake_case feature ID (e.g., `"dark_mode"`)

**Response on success:**
```json
{
  "feature_id": "dark_mode",
  "name": "Dark Mode Theme",
  "description": "Adds a theme toggle...",
  "status": "Testing",
  "traffic_percentage": 20,
  "last_modified": "2026-04-20",
  "targeted_segments": ["all"],
  "rollout_strategy": "ab_test"
}
```

**Response on error:**
```json
{
  "error": "FEATURE_NOT_FOUND",
  "message": "No feature with ID 'unknown' exists.",
  "feature_id": "unknown"
}
```

#### Tool 2: `set_feature_state`

**Parameters:**
- `feature_id` (string): Feature ID
- `state` (string): One of `"Disabled"`, `"Testing"`, `"Enabled"`

**Side effects:**
- `traffic_percentage` → 0 if Disabled, 100 if Enabled, 1-99 or 10 if Testing
- `last_modified` → today's date (YYYY-MM-DD)
- Dependency warnings if required dependencies are not Enabled

**Response:**
```json
{
  "feature_id": "search_v2",
  "status": "Enabled",
  "traffic_percentage": 100,
  "last_modified": "2026-04-27",
  "warnings": []
}
```

#### Tool 3: `adjust_traffic_rollout`

**Parameters:**
- `feature_id` (string): Feature ID
- `percentage` (integer): 0-100 (must be Testing status)

**Side effects:**
- `traffic_percentage` → new value
- `last_modified` → today's date
- Hint if percentage is 0% or 100%

**Response:**
```json
{
  "feature_id": "search_v2",
  "status": "Testing",
  "traffic_percentage": 50,
  "last_modified": "2026-04-27",
  "hint": null
}
```

## Testing

Run unit tests with pytest:

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

**Test Coverage:**
- 23 unit tests across 3 test files
- Happy path, error cases, edge cases
- Mocked HTTP client (no backend required)
- All tests passing ✓

**Test Files:**
- `tests/test_get_feature_info.py` — 6 tests
- `tests/test_set_feature_state.py` — 8 tests
- `tests/test_adjust_traffic_rollout.py` — 9 tests

## Error Handling

The server handles all error cases gracefully:

| Error Code | Cause | Status |
|---|---|---|
| `FEATURE_NOT_FOUND` | Feature ID doesn't exist | 404 |
| `INVALID_STATE` | State is not Disabled/Testing/Enabled | 400 |
| `INVALID_PERCENTAGE` | Percentage is not 0-100 integer | 400 |
| `WRONG_STATUS_FOR_ROLLOUT` | adjust_traffic only works on Testing | 400 |
| `BACKEND_UNREACHABLE` | Can't connect to ProShop API | Network error |
| `FILE_READ_ERROR` | ProShop can't read features.json | 500 |
| `FILE_WRITE_ERROR` | ProShop can't write features.json | 500 |

## Authentication

The server:
1. Reads credentials from environment variables on startup
2. Logs in to ProShop backend via `POST /api/users/login`
3. Caches JWT token for all subsequent requests
4. Auto-reauthenticates on 401 (Unauthorized)

Token lifetime: 30 days (configured in ProShop backend)

## Design Decisions

### Validation
- Input validation happens before API calls (fast fail)
- Backend validation is trusted for complex logic (dependencies, state transitions)

### Error Messages
- Network errors return structured dicts, never exceptions (LLM-friendly)
- Backend error responses are passed through verbatim

### State Management
- `AuthManager` is a singleton holding JWT token
- Token is cached until 401 or explicit reset
- Each tool invocation uses current cached token

### Testing
- All tests are unit tests with mocked HTTP client
- No integration tests (would require running backend)
- Fixtures provide sample feature objects for realistic scenarios

## File Structure Explained

| File | Purpose |
|---|---|
| `server.py` | FastMCP app entry point, three tool definitions, async main() |
| `client.py` | ProShopClient class wraps HTTP requests with auth headers |
| `auth.py` | AuthManager singleton handles login and token caching |
| `config.py` | Config dataclass loads and validates environment variables |
| `conftest.py` | Pytest fixtures: mocks, sample data, setup/teardown |

## Future Enhancements

- Add resource limits (e.g., max percentage change per adjustment)
- Implement feature flag diff/history tracking
- Add bulk operations (set state for multiple flags)
- Integrate with Slack for audit logging
- Extend with additional rollout strategies (gradual ramp-up)

---

**Last updated:** 2026-04-27  
**Python version:** 3.11  
**FastMCP version:** ≥2.0
