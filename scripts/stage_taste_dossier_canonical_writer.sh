#!/usr/bin/env bash
set -euo pipefail

mode="${1:-stage}"

stage_required_path() {
  local path="$1"
  if [ ! -e "$path" ]; then
    echo "Required canonical-writer path is missing: $path" >&2
    exit 1
  fi
  git add -A -- "$path"
}

stage_optional_path() {
  local path="$1"
  if [ -e "$path" ]; then
    git add -A -- "$path"
  fi
}

case "$mode" in
  stage)
    stage_required_path data/cache/taste_steam_review_dossiers
    stage_required_path data/production/pre_ai/taste_steam_review_dossier_work.json
    stage_required_path data/production/pre_ai/taste_steam_review_dossier_worker_index.json
    stage_required_path data/production/pre_ai/taste_steam_review_dossier_validation_status.json
    stage_required_path data/production/pre_ai/progressive_pass2_work.json
    stage_required_path data/ai_inbox/taste_steam_review_dossiers
    stage_required_path data/production/pre_ai/taste_steam_review_dossier_worker_groups

    # These paths are canonical when present, but are legitimately absent in some runs.
    # Stage them independently so one absent optional path cannot suppress the others.
    stage_optional_path data/control
    stage_optional_path data/quarantine
    stage_optional_path data/audit
    ;;
  assert-clean)
    status="$(git status --porcelain --untracked-files=all)"
    if [ -n "$status" ]; then
      echo "Canonical writer worktree is dirty after local commit:" >&2
      printf '%s\n' "$status" >&2
      exit 1
    fi
    ;;
  *)
    echo "Usage: $0 {stage|assert-clean}" >&2
    exit 2
    ;;
esac
