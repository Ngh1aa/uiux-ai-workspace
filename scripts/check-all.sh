#!/usr/bin/env bash
# Runs the checks from uiux-factory-ci.yml, skills-validate.yml and design-system.yml locally,
# continuing on failure, and prints one PASS/FAIL line per check.
# Usage: bash scripts/check-all.sh [repo-root]   (needs: pytest, pydantic, python-dotenv, node)
set -uo pipefail
ROOT="$(cd "${1:-.}" && pwd)" || exit 1
export PYTHONDONTWRITEBYTECODE=1
results=()
failures=0
run() {
  local name="$1"; shift
  local log; log="$(mktemp)"
  if ( "$@" ) >"$log" 2>&1; then
    results+=("PASS  $name")
  else
    failures=$((failures + 1))
    results+=("FAIL  $name")
    echo "---- FAIL: $name"
    tail -40 "$log"
  fi
  rm -f "$log"
}
S="$ROOT/skills_UIUX"; F="$ROOT/uiux-factory"
run "validate-skills"            bash -c "cd '$S' && python3 scripts/validate-skills.py"
run "validate-v2"                bash -c "cd '$S' && python3 scripts/validate-v2.py"
run "validate-flows"             bash -c "cd '$S' && python3 scripts/validate-flows.py"
run "validate-runtime-foundation" bash -c "cd '$S' && python3 -B scripts/validate-runtime-foundation.py"
run "validate-vendor-uiux-pro-max" bash -c "cd '$S' && python3 scripts/validate-vendor-uiux-pro-max.py"
run "visual-integrity-syntax"    bash -c "cd '$S' && node --check ui-craft-and-visual-qa/scripts/elementary-visual-integrity.mjs"
run "design-intelligence-smoke"  bash -o pipefail -c "cd '$S' && python3 -B design-intelligence-retrieval/scripts/query.py 'education admissions mobile' --design-system | grep . >/dev/null"
run "install-profile-dry"        bash -c "cd '$S' && python3 scripts/install-profile.py professional-core --target \$(mktemp -d) --dry-run"
run "install-project-dry"        bash -c "cd '$S' && python3 scripts/install-project.py examples/projects/qtsc --dry-run"
run "eval-harness-smoke"         bash -c "cd '$S' && python3 scripts/eval-harness.py smoke"
run "design-system:build-check"  bash -c "cd '$ROOT' && python3 design-system/scripts/build.py --check"
run "design-system:validate"     bash -c "cd '$ROOT' && python3 design-system/scripts/validate.py"
run "design-system:pytest"       bash -c "cd '$ROOT' && python3 -m pytest -q -p no:cacheprovider design-system/tests"
run "design-system:browser-gate" bash -c "cd '$ROOT' && node --test design-system/tests/browser-gate.test.cjs"
for v in $(sed -n 's/^ *python scripts\/\(validate_[a-z_]*\.py\).*/\1/p' "$ROOT/.github/workflows/uiux-factory-ci.yml" | sort -u); do
  run "factory:$v" bash -c "cd '$F' && python3 scripts/$v"
done
run "factory:pytest"             bash -c "cd '$F' && python3 -m pytest -q -p no:cacheprovider tests"
run "skills:pytest"              bash -c "cd '$S' && if ls tests >/dev/null 2>&1; then python3 -m pytest -q -p no:cacheprovider tests; else true; fi"
echo "======== SUMMARY"
printf '%s\n' "${results[@]}"
if (( failures > 0 )); then exit 1; fi
