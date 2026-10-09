#!/usr/bin/env bash
# Persist the complete deterministic current-cycle commercial boundary before
# any Dossier preparation, reconciliation, regression or Deep projection.
# An unsuccessful commercial push is fatal; Dossier must not run on unpersisted data.
set -euo pipefail

git config user.name "steam-kz-bot"
git config user.email "steam-kz-bot@users.noreply.github.com"
git add \
  data/cache/taste_fit.entry_index.json \
  data/production/pre_ai/store_snapshot.json \
  data/production/pre_ai/content_metadata.json \
  data/production/pre_ai/fixed_package_options.json \
  data/production/pre_ai/fx_snapshot.json \
  data/production/pre_ai/content_rules.json \
  data/production/pre_ai/family_graph.json \
  data/production/pre_ai/taste_projection.json \
  data/production/pre_ai/history_snapshot.json \
  data/production/pre_ai/deal_scenarios.json \
  data/production/pre_ai/chatgpt_payload.json \
  data/production/pre_ai/chatgpt_taste_queue.jsonl \
  data/production/pre_ai/chatgpt_purchase_context.jsonl \
  data/production/pre_ai/progressive_candidate_context.jsonl \
  data/production/pre_ai/progressive_pass1_work.json

git diff --cached --check
if git diff --cached --quiet; then
  echo "COMMERCIAL_PRE_AI_PERSISTED=already_current"
  exit 0
fi

git commit -m "Persist current deterministic commercial snapshot before Dossier"
for attempt in 1 2 3; do
  git fetch origin main:refs/remotes/origin/main
  if ! git rebase origin/main; then
    git rebase --abort || true
    echo "COMMERCIAL_PRE_AI_PERSISTED=failed_rebase"
    exit 1
  fi
  if git push origin HEAD:main; then
    echo "COMMERCIAL_PRE_AI_PERSISTED=updated"
    exit 0
  fi
  sleep $((attempt * 3))
done
echo "COMMERCIAL_PRE_AI_PERSISTED=failed_push"
exit 1
