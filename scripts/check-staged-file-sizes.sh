#!/usr/bin/env sh
set -eu

MAX_BYTES=$((15 * 1024 * 1024))

# NUL-delimited list of staged paths
staged=$(git diff --cached --name-only -z)

# Iterate NUL-delimited entries safely
printf "%s" "$staged" | while IFS= read -r -d '' path; do
  # size of staged blob (preferred)
  size=$(git cat-file -s ":$path" 2>/dev/null || true)
  if [ -z "$size" ]; then
    # fallback to working tree file size (may differ)
    if [ -f "$path" ]; then
      if stat --version >/dev/null 2>&1; then
        size=$(stat -c %s "$path" 2>/dev/null || echo "")
      else
        size=$(stat -f %z "$path" 2>/dev/null || echo "")
      fi
    fi
  fi

  if [ -n "$size" ] && [ "$size" -gt "$MAX_BYTES" ]; then
    mb=$(awk "BEGIN {printf \"%.2f\", $size/1024/1024}")
    maxmb=$(awk "BEGIN {printf \"%.2f\", $MAX_BYTES/1024/1024}")
    echo "ERROR: refusing to commit files larger than ${maxmb} MB" 1>&2
    echo "- $path (${mb} MB)" 1>&2
    echo "" 1>&2
    echo "If intentional, consider Git LFS or store large artifacts outside this repo." 1>&2
    exit 1
  fi
done
