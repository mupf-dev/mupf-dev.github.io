#!/usr/bin/env bash
# Erzeugt repos.json aus den öffentlichen, eigenen (nicht geforkten) Repositories.
set -euo pipefail
OWNER="${OWNER:-mupf-dev}"
OUT="${1:-repos.json}"

gh api --paginate "users/$OWNER/repos?per_page=100&type=owner" \
  | jq -s --arg owner "$OWNER" '
      add
      | map(select(.fork | not) | select(.private | not) | select(.name != ($owner + ".github.io")))
      | map({
          name,
          description,
          url: .html_url,
          pages: (if .has_pages then "https://\($owner).github.io/\(.name)/" else null end),
          homepage: (if (.homepage // "") == "" then null else .homepage end),
          language,
          topics,
          stars: .stargazers_count,
          archived,
          created: .created_at,
          updated: .pushed_at
        })
      | sort_by(.updated) | reverse
      | {owner: $owner, generated: (now | todate), repos: .}
    ' > "$OUT"
echo "$(jq '.repos | length' "$OUT") Repositories -> $OUT"
