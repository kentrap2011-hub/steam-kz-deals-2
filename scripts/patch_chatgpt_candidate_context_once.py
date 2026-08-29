from pathlib import Path

p = Path('scripts/build_pre_ai_chatgpt_payload.py')
text = p.read_text(encoding='utf-8')
changes = [
    (
        "        'schema_version': 2,\n        'purpose': 'chatgpt_consumer_bundle_with_strict_price_blind_taste_phase',",
        "        'schema_version': 3,\n        'purpose': 'chatgpt_consumer_bundle_with_context_bound_strict_price_blind_taste_phase',",
        'manifest schema',
    ),
    (
        "                    'taste_fingerprint': taste_row['taste_fingerprint'],\n                    'resolved_taste_fit': fit,",
        "                    'taste_fingerprint': taste_row['taste_fingerprint'],\n                    'candidate_context_sha256': taste_row['candidate_context_sha256'],\n                    'short_description': taste_row.get('short_description'),\n                    'bundle_members': taste_row.get('bundle_members') or [],\n                    'resolved_taste_fit': fit,",
        'cached semantic queue context',
    ),
    (
        "            'taste_fingerprint': taste_row['taste_fingerprint'],\n            'fit_tags': taste_row['fit_tags'],",
        "            'taste_fingerprint': taste_row['taste_fingerprint'],\n            'candidate_context_sha256': taste_row['candidate_context_sha256'],\n            'short_description': taste_row.get('short_description'),\n            'bundle_members': taste_row.get('bundle_members') or [],\n            'fit_tags': taste_row['fit_tags'],",
        'taste evaluation queue context',
    ),
    (
        "            'taste_model_version': taste_doc['current_binding']['taste_model_version'],\n        },",
        "            'taste_model_version': taste_doc['current_binding']['taste_model_version'],\n            'candidate_context_contract_blob_sha': taste_doc['current_binding']['candidate_context_contract_blob_sha'],\n            'content_metadata_blob_sha': taste_doc['current_binding']['content_metadata_blob_sha'],\n        },",
        'manifest profile/context binding',
    ),
    (
        "            'taste_phase_is_strictly_price_blind': True,\n            'taste_queue_forbids': ['price', 'discount', 'history', 'reviews', 'wishlist', 'popularity', 'deal_quality'],",
        "            'taste_phase_is_strictly_price_blind': True,\n            'candidate_context_digest_required_for_persisted_taste_verdict': True,\n            'steam_short_description_is_price_blind_candidate_evidence_not_profile_evidence': True,\n            'taste_queue_forbids': ['price', 'discount', 'history', 'reviews', 'wishlist', 'popularity', 'deal_quality'],",
        'manifest contract',
    ),
    (
        "        'source_family_count': len(families),\n        'ai_queue_count': len(ai_queue),",
        "        'source_family_count': len(families),\n        'candidate_description_known_count': taste_doc['candidate_context']['description_known_count'],\n        'candidate_description_missing_count': taste_doc['candidate_context']['description_missing_count'],\n        'candidate_description_coverage': taste_doc['candidate_context']['description_coverage'],\n        'ai_queue_count': len(ai_queue),",
        'manifest coverage',
    ),
]
for old, new, label in changes:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one fragment, found {count}')
    text = text.replace(old, new)
p.write_text(text, encoding='utf-8')
print('CHATGPT_CANDIDATE_CONTEXT_PATCH=PASS')
