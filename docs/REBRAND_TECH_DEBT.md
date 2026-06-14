# PiPa Rebrand — Remaining Technical Debt

This document lists internal identifiers that still use the upstream "Hermes" naming
and are intentionally **not renamed in Phase 1**. They are not visible to normal users
in the browser UI, but they exist in code, config, and storage.

Rename them in a future pass when the risk/effort is acceptable.

---

## Persisted Settings Migration (bot_name)

Existing installs that ran the original Hermes WebUI will have
`~/.hermes/webui/settings.json` containing `"bot_name": "Hermes"`.

**PiPa automatically migrates this at runtime:**

- `api/config.py` — `load_settings()` checks after merging disk state: if
  `bot_name` is missing, empty, or exactly `"Hermes"`, it is replaced with `"PiPa"`.
- `api/routes.py` — the settings-read (`/login` page) and settings-write
  (`POST /api/settings`) handlers apply the same migration guard.
- `static/boot.js` and `static/panels.js` — the frontend applies the same guard
  when it receives `bot_name` from the API, so even if the server returns the
  stale value the browser will show `"PiPa"`.

**Custom bot names are preserved:** any `bot_name` that is non-empty and not
exactly `"Hermes"` is treated as a real user preference and left untouched.

**To manually clear old state** if needed:
```bash
# Option 1: edit settings.json directly
python3 -c "
import json, pathlib
f = pathlib.Path.home() / '.hermes/webui/settings.json'
s = json.loads(f.read_text())
if s.get('bot_name') == 'Hermes':
    s['bot_name'] = 'PiPa'
    f.write_text(json.dumps(s, indent=2))
    print('Migrated')
else:
    print('Already OK:', s.get('bot_name'))
"
# Option 2: restart PiPa — load_settings() migrates automatically on each load
```

---

## Environment Variables (server-side)

These env vars control PiPa behavior but keep the `HERMES_WEBUI_*` prefix.
Changing them requires updating all Docker configs, `.env.example`, and any
existing user deployments.

| Variable | Purpose |
|---|---|
| `HERMES_WEBUI_PORT` | Port PiPa listens on |
| `HERMES_WEBUI_HOST` | Bind address |
| `HERMES_WEBUI_STATE_DIR` | Sessions, settings, projects storage |
| `HERMES_WEBUI_BOT_NAME` | Default assistant display name (now defaults to "PiPa") |
| `HERMES_WEBUI_AGENT_DIR` | Path to agent checkout |
| `HERMES_WEBUI_PYTHON` | Python interpreter path |
| `HERMES_WEBUI_PASSWORD` | Password hash for auth |
| `HERMES_WEBUI_SKIP_ONBOARDING` | Skip first-run wizard |
| `HERMES_WEBUI_TLS_CERT` / `_TLS_KEY` | TLS certificate paths |
| `HERMES_WEBUI_CHAT_BACKEND` | Toggle gateway vs legacy runtime |
| `HERMES_WEBUI_GATEWAY_BASE_URL` | Upstream gateway endpoint |
| `HERMES_WEBUI_GATEWAY_API_KEY` | Upstream gateway key |
| `HERMES_HOME` | Base Hermes home directory |
| `HERMES_CONFIG_PATH` | Path to upstream config.yaml |

## Browser localStorage Keys

These keys persist user preferences in the browser. Renaming them clears all
existing user preferences.

| Key | Purpose |
|---|---|
| `hermes-theme` | Light/dark/system theme |
| `hermes-skin` | Visual skin variant |
| `hermes-font-size` | Font size preference |
| `hermes-webui-model` | Last selected model |
| `hermes-panel-w` | Sidebar panel width |
| `hermes-raw-audio-mode` | Voice input mode |
| `hermes-voice-mode-button` | Voice mode button state |
| `hermes-tts-*` | TTS engine, voice, rate, pitch |
| `hermes-webui-workspace-*` | Workspace panel state |
| `hermes-kanban-active-board` | Active Kanban board |
| `hermes-sidebar-collapsed` | Sidebar collapsed state |
| `hermes-update-checked` / `hermes-update-dismissed` | Update banner state |
| `hermes-session-*` | Per-session state |
| `hermes-pinned-sessions` | Pinned session list |

## HTTP Request Header

`X-Hermes-CSRF-Token` — the CSRF protection header sent with every mutating
request. Renaming it requires changing both `static/boot.js` (sender) and
`api/auth.py` or wherever it is validated (receiver). Low risk to rename but
requires a coordinated change.

## Internal Python Identifiers

Function names, class names, and variable names in backend Python files that
reference "hermes" internally — e.g. `_run_agent_streaming`, `verify_hermes_imports`,
`hermes_command_exists`, `install_hermes_agent`, `HERMES_FOUND`. These are
internal implementation details not visible in the browser.

## Package and Repository Names

- `package.json` name: `"hermes-webui-devtools"` — dev-only ESLint tooling, not visible to users.
- `pyproject.toml` (if present) — any package name references.
- Git remote / repo URL — upstream is `nesquena/hermes-webui`.

## Internal Comments and Docstrings

Code comments referencing `Hermes` as context for the original upstream behavior.
These are intentionally preserved as attribution and architectural context.

## Upstream Runtime Function Names

- `_run_agent_streaming()` — core Hermes agent runner in `api/streaming.py`
- `_run_gateway_chat_streaming()` — gateway bridge in `api/gateway_chat.py`
- `webui_chat_backend_mode()` — backend selector
- `_webui_ephemeral_system_prompt()` — Hermes-specific prompt injection

These are part of the upstream Hermes runtime path that PiPa preserves as
a legacy/upstream option. Do not rename until the PiPa runtime fully replaces
the need for them.

## i18n Strings in Non-English Locales

`static/i18n.js` contains 18+ locale translations. The Phase 1 rebrand updated
the English (`en`) locale only. Other locales (Italian, Japanese, Russian,
Spanish, German, Chinese, Korean, French, Turkish, Polish, and more) still
contain `Hermes` in their translated strings. Update them when localisation
is revisited.
