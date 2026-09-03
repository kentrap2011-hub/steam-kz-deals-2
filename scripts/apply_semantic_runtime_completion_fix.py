import json
from pathlib import Path

from semantic_runtime_completion import (
    apply_payload_status,
    apply_visual_semantic_status,
    build_runtime_status,
)


def replace_once(path, old, new):
    text = path.read_text(encoding='utf-8')
    if new in text:
        return False
    if old not in text:
        raise SystemExit(f'Patch anchor missing in {path}: {old[:120]!r}')
    text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')
    return True


def patch_process_taste_inbox():
    path = Path('scripts/process_taste_inbox.py')
    changed = False
    changed |= replace_once(
        path,
        "from pathlib import Path\n\nINBOX_DIR = Path('data/ai_inbox/taste')",
        "from pathlib import Path\n\nfrom semantic_runtime_completion import build_runtime_status\n\nINBOX_DIR = Path('data/ai_inbox/taste')",
    )
    changed |= replace_once(
        path,
        "RECEIPT_DIR = Path('data/cache/taste_ingest_receipts')\nPROJECTION =",
        "RECEIPT_DIR = Path('data/cache/taste_ingest_receipts')\nLATEST_RUNTIME_STATUS = RECEIPT_DIR / 'latest_runtime_status.json'\nPROJECTION =",
    )
    changed |= replace_once(
        path,
        "    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n\n    for path in inbox_files:",
        "    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n\n    previous_runtime_status = load_json(LATEST_RUNTIME_STATUS) if LATEST_RUNTIME_STATUS.exists() else None\n    latest_runtime_status = build_runtime_status(receipt, previous_runtime_status)\n    LATEST_RUNTIME_STATUS.write_text(\n        json.dumps(latest_runtime_status, ensure_ascii=False, indent=2) + '\\n',\n        encoding='utf-8',\n    )\n\n    for path in inbox_files:",
    )
    return changed


def patch_pre_ai_builder():
    path = Path('scripts/build_pre_ai_chatgpt_payload.py')
    changed = False
    changed |= replace_once(
        path,
        "from taste_negative_contract import negative_readiness\n\nMAILING =",
        "from taste_negative_contract import negative_readiness\nfrom semantic_runtime_completion import apply_payload_status\n\nMAILING =",
    )
    changed |= replace_once(
        path,
        "TASTE_OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')\nMANIFEST_OUT =",
        "TASTE_OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')\nLATEST_RUNTIME_STATUS = Path('data/cache/taste_ingest_receipts/latest_runtime_status.json')\nMANIFEST_OUT =",
    )
    changed |= replace_once(
        path,
        "    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)\n    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')",
        "    latest_runtime_status = load(LATEST_RUNTIME_STATUS) if LATEST_RUNTIME_STATUS.exists() else None\n    apply_payload_status(manifest, latest_runtime_status)\n\n    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)\n    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')",
    )
    return changed


def patch_visual_builder():
    path = Path('scripts/build_visual_feed_v2.py')
    changed = False
    changed |= replace_once(
        path,
        "from card_explanation_policy import positive_reasons\nfrom russian_description_quality import classify_description",
        "from card_explanation_policy import positive_reasons\nfrom semantic_runtime_completion import apply_visual_semantic_status\nfrom russian_description_quality import classify_description",
    )
    changed |= replace_once(
        path,
        "    OUT.parent.mkdir(parents=True, exist_ok=True)\n    OUT.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')",
        "    apply_visual_semantic_status(output, payload)\n    OUT.parent.mkdir(parents=True, exist_ok=True)\n    OUT.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')",
    )
    return changed


def patch_final_visual_builder():
    path = Path('scripts/build_final_visual_payload.py')
    changed = False
    changed |= replace_once(
        path,
        "import refine_visual_ranking as refiner\n\nROOT = Path('.')",
        "import refine_visual_ranking as refiner\nfrom semantic_runtime_completion import apply_visual_semantic_status\n\nROOT = Path('.')",
    )
    changed |= replace_once(
        path,
        "OUT = ROOT / 'data/production/visual/current.json'\nDURATION_CONTRACT =",
        "OUT = ROOT / 'data/production/visual/current.json'\nSEMANTIC_PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'\nDURATION_CONTRACT =",
    )
    changed |= replace_once(
        path,
        "    ready = json.loads(before)\n    items = ready.get('items') or []",
        "    ready = json.loads(before)\n    semantic_payload = json.loads(SEMANTIC_PAYLOAD.read_text(encoding='utf-8')) if SEMANTIC_PAYLOAD.exists() else {}\n    apply_visual_semantic_status(ready, semantic_payload)\n    items = ready.get('items') or []",
    )
    changed |= replace_once(
        path,
        "    ready = base_builder.load_json(OUT)\n    ready['items'] = base_builder.achievement_quality.enrich_visual_items(ready.get('items') or [])",
        "    ready = base_builder.load_json(OUT)\n    apply_visual_semantic_status(ready, payload)\n    ready['items'] = base_builder.achievement_quality.enrich_visual_items(ready.get('items') or [])",
    )
    return changed


def bootstrap_latest_runtime_status():
    receipt_dir = Path('data/cache/taste_ingest_receipts')
    receipt_dir.mkdir(parents=True, exist_ok=True)
    candidates = []
    for path in receipt_dir.glob('*.json'):
        if path.name == 'latest_runtime_status.json':
            continue
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        if doc.get('status') == 'complete' and doc.get('processed_at_utc'):
            candidates.append((doc['processed_at_utc'], path, doc))
    if not candidates:
        return None
    _stamp, _path, receipt = max(candidates, key=lambda row: row[0])
    latest_path = receipt_dir / 'latest_runtime_status.json'
    previous = json.loads(latest_path.read_text(encoding='utf-8')) if latest_path.exists() else None
    latest = build_runtime_status(receipt, previous)
    latest_path.write_text(json.dumps(latest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return latest


def refresh_current_status_artifacts(latest_runtime_status):
    payload_path = Path('data/production/pre_ai/chatgpt_payload.json')
    if not payload_path.exists():
        raise SystemExit('Canonical chatgpt_payload.json is missing')
    payload = json.loads(payload_path.read_text(encoding='utf-8'))
    apply_payload_status(payload, latest_runtime_status)
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    visual_path = Path('data/production/visual/current.json')
    if visual_path.exists():
        visual = json.loads(visual_path.read_text(encoding='utf-8'))
        apply_visual_semantic_status(visual, payload)
        visual_path.write_text(json.dumps(visual, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def main():
    changed = {
        'process_taste_inbox': patch_process_taste_inbox(),
        'pre_ai_builder': patch_pre_ai_builder(),
        'visual_builder': patch_visual_builder(),
        'final_visual_builder': patch_final_visual_builder(),
    }
    latest = bootstrap_latest_runtime_status()
    refresh_current_status_artifacts(latest)
    print(json.dumps({'status': 'patched', 'code_changes': changed}, indent=2))


if __name__ == '__main__':
    main()
