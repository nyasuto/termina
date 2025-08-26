# Repository Guidelines

## Most Importrant Policy
- 技術的に難しいポイントはo3に聞く
- ユーザとの対話は必ず日本語で行う

## Project Structure & Module Organization
- `termina.py`: Entry point. Defines `TerminaApp` (menu bar UI, hotkeys, record/transcribe/paste flow).
- `speech_providers.py`: Provider factory and implementations (OpenAI API, local Whisper).
- `ffmpeg_processor.py`: Optional FFmpeg-based noise reduction and filters.
- `whisper_models.py`: Local model metadata and management helpers.
- `tests/`: Pytest suite (`test_*.py`).
- Tooling: `pyproject.toml` (deps, ruff, pytest, mypy), `Makefile` (dev workflow), `.env.local` (secrets).

## Build, Test, and Development Commands
- `make dev-setup`: Sync deps (via `uv`); sets up dev env.
- `make run`: Launch app with `uv`.
- `make test`: Run pytest with coverage (term + xml + htmlcov).
- `make lint` / `make lint-check`: Ruff lint/format (fix vs. check-only).
- `make format`: Apply ruff formatter.
- `make security`: Ruff security rules + `pip-audit`.
- `make check`: Lockfile check, quality, tests.
- Alternatives: `uv sync`, `uv run pytest -v`.

## Coding Style & Naming Conventions
- Python 3.9+, 4-space indent, max line length 88, double quotes (ruff formatter).
- Lint: ruff rules `E,W,F,UP,B,SIM,I,N,S`; see `pyproject.toml` ignores.
- Names: `snake_case` functions/vars, `PascalCase` classes, `CONSTANT_CASE` constants, modules as single-file components.
- Prefer small, focused functions; keep UI logic in `TerminaApp`, audio in `ffmpeg_processor`, and provider logic in `speech_providers`.

## Testing Guidelines
- Framework: pytest; tests in `tests/`, files `test_*.py`.
- Run: `make test` or `uv run pytest`.
- Write fast, side-effect-free tests; avoid macOS UI side effects—mock subprocess/`osascript` and network.
- Aim to cover new logic and error paths; keep existing coverage healthy (XML written to `coverage.xml`).

## Commit & Pull Request Guidelines
- Conventional commits: `feat:`, `fix:`, `docs:`, `ci:`, etc. (seen in history).
- Branch names: `feat/...`, `fix/...`, `docs/...` (match PR scope).
- PRs: clear description, linked issues, test evidence (logs or screenshots), note macOS-specific behavior, and update README if user-facing.
- All checks must pass: lint/format, security, tests, lockfile check (`make check`).

## Security & Configuration Tips
- `.env.local` required for OpenAI: `OPENAI_API_KEY=...`; select provider via `SPEECH_PROVIDER` (`openai` or local).
- macOS permissions: Microphone and Accessibility are required for recording and paste.
- FFmpeg recommended for noise reduction (`brew install ffmpeg`).
