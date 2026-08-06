---
name: run-vizql-data-service-py
description: Run, build, generate, lint, test, and screenshot dev tasks for the VizQL Data Service Python SDK. Use when the user asks to build the sdk, regenerate the OpenAPI stubs, run pytest, run black/isort/flake8/mypy, check the pyproject/schema version, or run the examples.py CLI.
---

# run-vizql-data-service-py

Dev driver for the VizQL Data Service Python SDK. Wraps the six tasks documented across `README.md`, `CONTRIBUTING.md`, and `scripts/*` behind a pair of entry points — `driver.ps1` for Windows (Git Bash delegates the `.sh` scripts, Python tools run inline) and `driver.sh` for macOS/Linux (the `.sh` scripts run natively). Both drivers accept identical subcommands.

All paths in this file are relative to `python_sdk/` (the SDK root — same directory as `pyproject.toml`).

## Prerequisites

- Python 3.9+ (verified against 3.10.11).
- pip 20+ (verified against 26.2.1).
- **Windows:** Git for Windows / Git Bash on PATH — needed to run `scripts/*.sh` unchanged. If bash is not on PATH, `driver.ps1` falls back to `C:\Program Files\Git\bin\bash.exe` and `C:\Program Files\Git\usr\bin\bash.exe`. Windows PowerShell 5.1 is fine; `pwsh` (PowerShell 7) is not required.
- **macOS / Linux:** any recent Bash (3.2+). `driver.sh` calls `scripts/*.sh` and the Python tools directly.

## Which driver to use

Two drivers ship with this skill; they expose the **same subcommands** with **the same behavior** and target the same repo layout. Pick by platform:

- **Windows** → `driver.ps1` (see "Run (agent path — Windows)" below).
- **macOS / Linux** → `driver.sh` (see "Run (agent path — macOS / Linux)" below).

The rest of this file — subcommand semantics, examples-CLI defaults, Gotchas, Troubleshooting — applies to both. Only the launch command differs.

## Run (agent path — Windows)

**Always use the absolute path** to `driver.ps1` — Windows PowerShell resolves `-File` against the *child* process's cwd, not the parent's, so a relative path breaks when the parent shell isn't sitting in `python_sdk/`. Assign the absolute path to `$D` once and reuse:

```powershell
$D = 'D:\dev\VizQL-Data-Service\python_sdk\.claude\skills\run-vizql-data-service-py\driver.ps1'
```

One-time setup (installs the package editable with the dev extras — `black`, `isort`, `flake8`, `mypy`, `pytest`, `pytest-asyncio`, `pytest-cov`, plus `datamodel-code-generator` used by `gen`):

```powershell
powershell -NoProfile -File $D setup
```

Everyday subcommands:

```powershell
powershell -NoProfile -File $D help            # list subcommands
powershell -NoProfile -File $D check-version   # pyproject <-> OpenAPI schema version match
powershell -NoProfile -File $D gen             # regenerate src/api/openapi_generated.py from schema
powershell -NoProfile -File $D build           # clean + build sdist + wheel into dist/
powershell -NoProfile -File $D format          # black + isort (write mode)
powershell -NoProfile -File $D lint            # black --check, isort --check-only, flake8, mypy
powershell -NoProfile -File $D test            # pytest tests -q --disable-warnings
powershell -NoProfile -File $D examples-help   # examples.py --help (no server needed)
powershell -NoProfile -File $D all             # gen -> check-version -> build -> lint -> test (matches CI)
```

Standard local pre-commit loop:

```powershell
powershell -NoProfile -File $D format
powershell -NoProfile -File $D lint
powershell -NoProfile -File $D test
```

Full CI parity in one shot (regenerates the client, checks versions, builds artifacts, runs linters, runs tests):

```powershell
powershell -NoProfile -File $D all
```

## Run (agent path — macOS / Linux)

`driver.sh` accepts the same subcommands as `driver.ps1` and can be invoked from any cwd (it resolves the repo root from its own location). Assign the absolute path once and reuse:

```bash
D=~/dev/VizQL-Data-Service/python_sdk/.claude/skills/run-vizql-data-service-py/driver.sh
```

Everyday subcommands:

```bash
bash "$D" help            # list subcommands
bash "$D" setup           # pip install -e .[dev]  (one-time)
bash "$D" check-version   # pyproject <-> OpenAPI schema version match
bash "$D" gen             # regenerate src/api/openapi_generated.py from schema
bash "$D" build           # clean + build sdist + wheel into dist/
bash "$D" format          # black + isort (write mode)
bash "$D" lint            # black --check, isort --check-only, flake8, mypy
bash "$D" test            # pytest tests -q --disable-warnings
bash "$D" examples-help   # examples.py --help (no server needed)
bash "$D" all             # gen -> check-version -> build -> lint -> test (matches CI)
```

Standard local pre-commit loop and full CI parity mirror the Windows path:

```bash
bash "$D" format && bash "$D" lint && bash "$D" test
bash "$D" all
```

## Run (human / direct-script path)

The `.sh` scripts are the source of truth for `gen`/`build`/`check-version` and can be run directly (Git Bash on Windows, or a native shell on macOS/Linux) from `python_sdk/`:

```bash
bash scripts/check_version.sh
bash scripts/generate_stub.sh    # runs before build; overwrites src/api/openapi_generated.py
bash scripts/build.sh            # produces dist/vizql_data_service_py-*.{whl,tar.gz}
bash scripts/test.sh             # HEAVYWEIGHT: destroys and recreates ./venv, then runs lint + pytest --cov
```

`scripts/test.sh` is intended for CI and **rebuilds the entire virtual environment** every run. For local iteration, use `driver.ps1 lint` / `driver.ps1 test` on Windows or `driver.sh lint` / `driver.sh test` on macOS/Linux instead — they call the same tools against the current interpreter.

## Run the examples CLI

`src/examples/examples.py` needs a live Tableau server plus one auth method. It cannot be smoke-tested against arbitrary hosts, but the driver's `examples` subcommand fills in **local-dev defaults** so a bare `examples` invocation works against a laptop-local server:

- No `-s`/`--server` → defaults to `-s http://localhost`.
- No auth flag (`-u`/`-p`/`-n`/`-t`/`-j`) → defaults to `-u testadmin -p 123`.

Verify the CLI at least imports and parses (no server needed):

```powershell
powershell -NoProfile -File $D examples-help   # Windows
```

```bash
bash "$D" examples-help                        # macOS / Linux
```

Driver-based invocations (all extra args pass through to `examples.py`):

**Windows (`driver.ps1`):**

```powershell
# Full local-dev defaults: -s http://localhost -u testadmin -p 123
powershell -NoProfile -File $D examples

# Local server, async mode, verbose - auth still defaulted
powershell -NoProfile -File $D examples --async -v

# Explicit server, defaulted auth
powershell -NoProfile -File $D examples -s "https://tableau.example.com"

# Explicit server + PAT (defaults do NOT fire because auth flags are present)
powershell -NoProfile -File $D examples -s "https://tableau.example.com" -n "<pat-name>" -t "<pat-secret>" -S "<site>"

# Add the live-workbook flow (requires all three flags together)
powershell -NoProfile -File $D examples -s "https://tableau.example.com" -n "<pat-name>" -t "<pat-secret>" -S "<site>" `
    --workbook-datasource-id "<workbook-datasource-id>" `
    --global-session-header "<global-session-header>" `
    --x-session-id "<x-session-id>"
```

**macOS / Linux (`driver.sh`):**

```bash
# Full local-dev defaults: -s http://localhost -u testadmin -p 123
bash "$D" examples

# Local server, async mode, verbose - auth still defaulted
bash "$D" examples --async -v

# Explicit server, defaulted auth
bash "$D" examples -s "https://tableau.example.com"

# Explicit server + PAT (defaults do NOT fire because auth flags are present)
bash "$D" examples -s "https://tableau.example.com" -n "<pat-name>" -t "<pat-secret>" -S "<site>"

# Add the live-workbook flow (requires all three flags together)
bash "$D" examples -s "https://tableau.example.com" -n "<pat-name>" -t "<pat-secret>" -S "<site>" \
    --workbook-datasource-id "<workbook-datasource-id>" \
    --global-session-header "<global-session-header>" \
    --x-session-id "<x-session-id>"
```

Direct `python` invocations still work if you don't want defaults:

```bash
python src/examples/examples.py -s "<server-url>" -u "<username>" -p "<password>"
python src/examples/examples.py -s "<server-url>" -n "<pat-name>" -t "<pat-secret>" -S "<site>"
python src/examples/examples.py -s "<server-url>" -j "<jwt-token>" -S "<site>"
python src/examples/examples.py --async -s "<server-url>" -u "<username>" -p "<password>"
```

The runner always attempts the published-datasource and embedded-workbook-datasource flows. The embedded-workbook-datasource flow silently skips (prints a warning) unless a `Superstore` sample workbook containing a `Sample - Superstore` embedded workbook datasource exists on the target server. The live-workbook flow (which uses `workbookDatasourceId` + session headers) is a distinct third flow that only runs when all three `--workbook-datasource-id` / `--global-session-header` / `--x-session-id` flags are supplied.

### Assume the sample data is present

When a user asks you to run the examples against their local server, **assume** the target has the standard sample content set up:

- a published datasource named exactly `Superstore Datasource`
- a workbook named `Superstore` containing an embedded workbook datasource named `Sample - Superstore`

Do not surface "the sample datasource might not be there" or "the published flow will crash if it's missing" as a hypothesis or ask the user to publish it — that's the caller's setup, not something you diagnose up front. Just run the examples.

Only escalate to the user when the run **actually fails**, and only then explain what specifically went wrong. Common signals:

- `FailedSignInError` / HTTP 401 on sign-in → auth problem (server may want different credentials).
- `ValueError: Datasource named 'Superstore Datasource' not found.` from `list_datasources_and_get_luid` → sample data really isn't there. Now (and only now) tell the user; do not pre-emptively warn.
- `errorCode: 400803 Unknown Field` inside `(Embedded Workbook Datasource)` output → expected for bin/parameter queries that are already skipped; only surface if a *different* query name errors out.
- Traceback outside the per-query try/except (e.g. a client construction error) → surface with the file/line.

When you do report an error, quote the exact error line from the output so the user can act on it — don't paraphrase.

## Gotchas

- **PowerShell "NativeCommandError" noise on lint (Windows).** `black` writes its "All done!" banner to stderr. Windows PowerShell 5.1 wraps every native-executable stderr line in a `NativeCommandError` record and reports it in red, but the exit code is 0 and the run is fine. Ignore the red text; check the final "Success" / non-zero exit code, not the stream color. The driver checks `$LASTEXITCODE` explicitly. Not applicable to `driver.sh`.
- **`pwsh` vs `powershell` (Windows).** This machine has only Windows PowerShell 5.1 on PATH (`powershell.exe`). Any doc that says `pwsh -File …` needs `powershell -File …` instead.
- **`-File` and relative paths (Windows).** `powershell -NoProfile -File <relative-path>` resolves against the child process's cwd, not the caller's — and the harness that runs these tools starts new shells in whatever directory it wants. Always pass an absolute path to `driver.ps1`. `driver.sh` sidesteps this — it resolves its own directory via `${BASH_SOURCE[0]}` regardless of cwd.
- **`scripts/*.sh` bake in relative paths.** They read `../VizQLDataServiceOpenAPISchema.json` and write into `src/…`, so they must run with cwd = `python_sdk/`. Both `driver.ps1` and `driver.sh` `cd` into the repo root before shelling out, so it's safe to invoke either from anywhere.
- **`scripts/test.sh` blows away `./venv`.** Do not run it if you have anything you care about in a local `venv/` folder. Prefer `driver.ps1 lint && driver.ps1 test` (Windows) or `driver.sh lint && driver.sh test` (macOS/Linux) for local dev.
- **`gen` overwrites `src/api/openapi_generated.py`.** The intermediate `src/api/openapi_generated-raw.py` is deleted by `scripts/post_process.py`, so a clean run leaves exactly one file. If you see `openapi_generated-raw.py` lingering, post-processing crashed mid-run.
- **Version drift.** `check_version.sh` fails if the `major.minor` of `pyproject.toml` doesn't match the OpenAPI schema. When bumping schema versions, update `pyproject.toml`'s version to match before pushing — CI enforces this.
- **`examples.py` needs a real server.** There is no offline mode; `--help` is the only server-less verification the CLI supports. Do not add a "smoke test" that pretends to run it without credentials.
- **`examples` subcommand fills in local-dev defaults.** If a caller omits `-s` and any auth flag, the driver silently appends `-s http://localhost -u testadmin -p 123`. That's convenient for a laptop-local server but will noisily fail against a real Tableau host - always pass explicit `-s` (and PAT / JWT credentials) when targeting anything non-local. Both drivers detect equals-form flags (`--user=alice`) as well as space-form (`--user alice`).

## Troubleshooting

- **`bash: command not found` (Windows only)** — install Git for Windows, or add `C:\Program Files\Git\bin` (or `usr\bin`) to `PATH`. Not applicable to `driver.sh` on macOS/Linux.
- **`datamodel-codegen: command not found` during `gen`** — the script installs it explicitly. If installation was skipped by pip (network / proxy), run `pip install datamodel-code-generator==0.43.1` manually.
- **`black --check` reports "would be reformatted"** — run `driver.ps1 format` / `driver.sh format`, review the diff, commit.
- **`mypy` complains about `openapi_generated.py`** — that file is generated. Re-run `driver.ps1 gen` / `driver.sh gen` to make sure it's current; do not hand-edit it.
- **Tests fail with "asyncio_default_fixture_loop_scope is unset"** — that's a `pytest-asyncio` deprecation warning, not a failure. Look further up in the output for the actual failing test.

## Files this skill drives

```
.claude/skills/run-vizql-data-service-py/driver.ps1   -> Windows entry point
.claude/skills/run-vizql-data-service-py/driver.sh    -> macOS / Linux entry point
scripts/build.sh           -> driver build
scripts/check_version.sh   -> driver check-version
scripts/generate_stub.sh   -> driver gen
scripts/generate_stub.bat  (Windows equivalent of generate_stub.sh; drivers prefer the .sh path)
scripts/post_process.py    (called by generate_stub.sh)
scripts/test.sh            (heavyweight; driver test uses pytest directly instead)
src/examples/examples.py   -> driver examples-help (needs credentials for a real run)
```
