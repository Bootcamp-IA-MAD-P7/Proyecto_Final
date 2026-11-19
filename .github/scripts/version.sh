# Next beta tag for HEAD (CONTRIBUTING §9). Sourced by tags.yml and ci.yml.
# next_beta sets $tag (empty when the new commits do not change the version) and $reason.

# Commits that change the version: breaking, feat, fix or perf.
VERSIONED='^[a-z]+(\([^)]*\))?!:|^(feat|fix|perf)(\([^)]*\))?:'

# Change level of a commit range: major, minor, patch or none.
bump() {
  local log
  log=$(git log --format='%s%n%b' "$1")
  if grep -qE '^[a-z]+(\([^)]*\))?!:|^BREAKING[ -]CHANGE:' <<< "$log"; then echo major
  elif grep -qE '^feat(\([^)]*\))?:' <<< "$log"; then echo minor
  elif grep -qE '^(fix|perf)(\([^)]*\))?:' <<< "$log"; then echo patch
  else echo none
  fi
}

next_beta() {
  local prev range last level version major minor patch n commits
  tag='' reason=''

  # Tag only when the commits since the last beta change the version.
  prev=$(git describe --tags --abbrev=0 --match 'v*-beta.*' 2>/dev/null || true)
  range="${prev:+$prev..}HEAD"
  if [ "$(bump "$range")" = none ]; then return 0; fi

  # Next stable version from the commits since the last stable tag.
  last=$(git tag --list 'v[0-9]*' --sort=-v:refname | grep -v -- - | head -n 1 || true)
  if [ -z "$last" ]; then
    version=0.1.0
    level="first version"
  else
    level=$(bump "$last..HEAD")
    IFS=. read -r major minor patch <<< "${last#v}"
    case "$level" in
      major)
        if [ "$major" -eq 0 ]; then minor=$((minor + 1)); else major=$((major + 1)); minor=0; fi
        patch=0 ;;
      minor) minor=$((minor + 1)); patch=0 ;;
      *) patch=$((patch + 1)) ;;
    esac
    version="$major.$minor.$patch"
    level="$level since $last"
  fi

  n=$(git tag --list "v$version-beta.*" | sed 's/.*-beta\.//' | sort -n | tail -n 1)
  tag="v$version-beta.$(( ${n:-0} + 1 ))"
  commits=$(git log --format='%s' "$range" | grep -E "$VERSIONED" | sed 's/^/- /' || true)
  reason="$level"$'\n'"$commits"
}
