#!/usr/bin/env bash
# Creates or updates on GitHub the rulesets of .github/rulesets/ that protect dev and main (make github-protect).
# Each file is named after its ruleset ("name" in the JSON), so running it again updates instead of duplicating.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

for file in .github/rulesets/*.json; do
  name=$(basename "$file" .json)
  id=$(gh api "repos/{owner}/{repo}/rulesets" --jq ".[] | select(.name == \"$name\") | .id")
  if [ -n "$id" ]; then
    gh api --method PUT "repos/{owner}/{repo}/rulesets/$id" --input "$file" > /dev/null
    echo "Updated ruleset $name"
  else
    gh api --method POST "repos/{owner}/{repo}/rulesets" --input "$file" > /dev/null
    echo "Created ruleset $name"
  fi
done
