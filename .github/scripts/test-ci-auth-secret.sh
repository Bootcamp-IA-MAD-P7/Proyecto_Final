#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
if windows_root=$(cd "$repo_root" && pwd -W 2>/dev/null); then
  repo_root="$windows_root"
fi
temporary_dir=$(mktemp -d)
trap 'rm -rf "$temporary_dir"' EXIT

secret_log="$temporary_dir/secrets"

cat > "$temporary_dir/docker" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ " $* " == *" build "* ]]; then
  [[ -n "${AUTH_SECRET:-}" && ${#AUTH_SECRET} -ge 32 ]] || exit 1
  printf '%s\n' "$AUTH_SECRET" >> "$CI_AUTH_SECRET_LOG"
  exit 0
fi
if [[ " $* " == *" up -d --build "* ]]; then
  [[ -n "${AUTH_SECRET:-}" ]] && exit 0
  exit 1
fi
exit 1
EOF
chmod +x "$temporary_dir/docker"

for _ in 1 2; do
  AUTH_SECRET= CI_AUTH_SECRET_LOG="$secret_log" PATH="$temporary_dir:$PATH" \
    make -C "$repo_root" ci-production-build \
      COMPOSE_PROD="docker compose -f compose.yaml -f compose.production.yaml" >/dev/null
done

mapfile -t secrets < "$secret_log"
if [[ ${#secrets[@]} -ne 2 || "${secrets[0]}" == "${secrets[1]}" ]]; then
  echo "CI authentication secrets must be generated per production build" >&2
  exit 1
fi

for mode in absent empty; do
  if [[ "$mode" == absent ]]; then
    if (unset AUTH_SECRET; PATH="$temporary_dir:$PATH" make -C "$repo_root" up-prod COMPOSE_PROD="docker compose -f compose.yaml -f compose.production.yaml") >/dev/null 2>&1; then exit 1; fi
  elif AUTH_SECRET= PATH="$temporary_dir:$PATH" make -C "$repo_root" up-prod COMPOSE_PROD="docker compose -f compose.yaml -f compose.production.yaml" >/dev/null 2>&1; then exit 1; fi
done
