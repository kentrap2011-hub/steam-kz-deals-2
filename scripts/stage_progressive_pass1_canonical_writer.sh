#!/usr/bin/env bash
set -euo pipefail

git add -A -- \
  data/ai_inbox/progressive_pass1 \
  data/cache/progressive_pass1_state.json \
  data/cache/progressive_pass1_receipts \
  data/production/pre_ai/progressive_pass1_work.json \
  data/production/pre_ai/progressive_pass2_work.json \
  data/cache/taste_steam_review_dossiers \
  data/production/pre_ai/taste_steam_review_dossier_work.json \
  data/production/pre_ai/taste_steam_review_dossier_worker_index.json \
  data/production/pre_ai/taste_steam_review_dossier_validation_status.json \
  data/production/pre_ai/taste_steam_review_dossier_worker_groups

stage_optional_path() {
  local path="$1"
  if [[ -e "$path" || -L "$path" ]] || git ls-files -- "$path" | grep -q .; then
    git add -A -- "$path"
  fi
}

stage_optional_path data/ai_inbox/taste_steam_review_dossiers
stage_optional_path data/quarantine/taste_steam_review_dossier_inbox
stage_optional_path data/audit/taste_steam_review_dossier_group_failures.jsonl
