#!/usr/bin/env bash
# driver.sh - dev driver for the VizQL Data Service Python SDK (macOS / Linux).
#
# Runs from python_sdk/ (or any cwd; script resolves paths from its own location).
# .sh scripts under scripts/ are called directly; Python / pip / lint tools run inline.
#
# Usage:
#   bash .claude/skills/run-vizql-data-service-py/driver.sh <subcommand> [args...]
#
# Subcommands:
#   setup            Install package in editable mode with [dev] extras.
#   check-version    Verify pyproject.toml <-> OpenAPI schema major.minor match.
#   gen              Regenerate src/api/openapi_generated.py from the schema.
#   build            Clean, build sdist + wheel into dist/.
#   format           Apply black + isort (writes changes).
#   lint             Run black --check, isort --check-only, flake8, mypy.
#   test             Run pytest against tests/.
#   examples-help    Print examples.py CLI help (no server needed).
#   examples         Run examples.py; extra args are forwarded (e.g. -s <url> --async).
#                    If no -s/--server is given, defaults to -s http://localhost.
#                    If no auth flag (-u/-p/-n/-t/-j) is given, defaults to
#                    -u testadmin -p 123.
#   all              gen -> check-version -> build -> lint -> test  (matches CI).
#   help             Show this help.

set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SKILL_ROOT/../../.." && pwd)"
cd "$REPO_ROOT"

log()  { printf '\033[36m[driver] %s\033[0m\n' "$*"; }
warn() { printf '\033[33m[driver] %s\033[0m\n' "$*"; }

run_step() {
    local label="$1"; shift
    log "$label"
    "$@"
}

cmd_setup() {
    run_step "python -m pip install --upgrade pip" python -m pip install --upgrade pip
    run_step "pip install -e .[dev]"               pip install -e ".[dev]"
}

cmd_check_version() { run_step "bash scripts/check_version.sh" bash scripts/check_version.sh; }
cmd_gen()           { run_step "bash scripts/generate_stub.sh" bash scripts/generate_stub.sh; }
cmd_build()         { run_step "bash scripts/build.sh"         bash scripts/build.sh; }

cmd_format() {
    run_step "black ."  black .
    run_step "isort ."  isort .
}

cmd_lint() {
    run_step "black --check"      black . --check
    run_step "isort --check-only" isort . --check-only
    run_step "flake8"             flake8 .
    run_step "mypy"               mypy .
}

cmd_test()          { run_step "pytest" pytest tests -q --disable-warnings; }
cmd_examples_help() { run_step "examples.py --help" python src/examples/examples.py --help; }

# Match on the flag *name* only, so both space-form (`-u alice`) and
# equals-form (`--user=alice`) are detected. Without splitting on '=',
# `--user=alice` would slip past and the driver would silently override
# it with the injected default credentials.
cmd_examples() {
    local auth_flags=(-u --user -p --password -n --pat-name -t --pat-secret -j --jwt-token)
    local server_flags=(-s --server)
    local has_auth=0 has_server=0

    local tok name
    for tok in "$@"; do
        name="${tok%%=*}"
        if [[ $has_auth -eq 0 ]]; then
            for f in "${auth_flags[@]}"; do
                [[ "$name" == "$f" ]] && { has_auth=1; break; }
            done
        fi
        if [[ $has_server -eq 0 ]]; then
            for f in "${server_flags[@]}"; do
                [[ "$name" == "$f" ]] && { has_server=1; break; }
            done
        fi
    done

    local final_args=(src/examples/examples.py "$@")
    if [[ $has_server -eq 0 ]]; then
        warn "no -s/--server supplied - defaulting to -s http://localhost"
        final_args+=(-s http://localhost)
    fi
    if [[ $has_auth -eq 0 ]]; then
        warn "no auth flag supplied - defaulting to -u testadmin -p 123"
        final_args+=(-u testadmin -p 123)
    fi

    log "examples.py $*"
    python "${final_args[@]}"
}

cmd_all() {
    cmd_gen
    cmd_check_version
    cmd_build
    cmd_lint
    cmd_test
}

cmd_help() {
    # Print the leading '#' comment block of this script, skipping the shebang.
    sed -n '2,25{/^#/{s/^# \{0,1\}//;p;};}' "$SKILL_ROOT/driver.sh"
}

subcommand="${1:-help}"
shift || true

case "$subcommand" in
    setup)         cmd_setup ;;
    check-version) cmd_check_version ;;
    gen)           cmd_gen ;;
    build)         cmd_build ;;
    format)        cmd_format ;;
    lint)          cmd_lint ;;
    test)          cmd_test ;;
    examples-help) cmd_examples_help ;;
    examples)      cmd_examples "$@" ;;
    all)           cmd_all ;;
    help|--help|-h) cmd_help ;;
    *)
        printf 'unknown subcommand: %s\n\n' "$subcommand" >&2
        cmd_help
        exit 2
        ;;
esac
