#!/usr/bin/env bash
# Creates or updates on GitHub the labels of docs/ISSUE_LABELS.md, their source of truth (make labels).
set -euo pipefail

file="$(git rev-parse --show-toplevel)/docs/ISSUE_LABELS.md"

# Label rows of its tables: | `name` | use | `COLOR` |
grep -E '^\| `[^`]+` \|.*\| `[0-9A-Fa-f]{6}` \|$' "$file" | while IFS='|' read -r _ name use color _; do
  name=$(sed -E 's/^ *`(.*)` *$/\1/' <<< "$name")
  color=$(sed -E 's/^ *`(.*)` *$/\1/' <<< "$color")
  # Plain-text description: no Markdown links or backticks, and at most 100 characters (GitHub limit).
  description=$(sed -E 's/\[([^]]*)\]\([^)]*\)/\1/g; s/`//g; s/^ +//; s/ +$//' <<< "$use")
  gh label create "$name" --description "${description:0:100}" --color "$color" --force
done
