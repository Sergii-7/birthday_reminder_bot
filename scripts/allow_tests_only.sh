#!/usr/bin/env bash
set -euo pipefail

allow() {
  local f="$1"
  [[ "$f" =~ ^tests/ ]] \
  || [[ "$f" =~ ^scripts/ ]] \
  || [[ "$f" == "pytest.ini" ]] \
  || [[ "$f" == "conftest.py" ]] \
  || [[ "$f" == "tox.ini" ]] \
  || [[ "$f" == "noxfile.py" ]] \
  || [[ "$f" == "pyproject.toml" ]] \
  || [[ "$f" == "requirements.txt" ]] \
  || [[ "$f" == "requirements-dev.txt" ]] \
  || [[ "$f" == ".pre-commit-config.yaml" ]] \
  || [[ "$f" == "README.md" ]] \
  || [[ "$f" =~ ^\.github/ ]] \
  || [[ "$f" =~ ^\.idea/ ]] \
  || [[ "$f" =~ ^\.vscode/ ]]
}

staged="$(git diff --cached --name-only --diff-filter=ACMR)" || exit 0

violations=()
while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  if ! allow "$file"; then
    violations+=("$file")
  fi
done <<< "$staged"

if (( ${#violations[@]} > 0 )); then
  echo "❌ Заборонені зміни поза tests/:"
  for v in "${violations[@]}"; do echo "  - $v"; done
  echo "Дозволені лише: tests/** та кілька конфігів (див. scripts/allow_tests_only.sh)."
  echo "Прибери з індексу:  git restore --staged <file>"
  exit 1
fi

exit 0
