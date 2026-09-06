import json
from pathlib import Path

CONTRACT_PATH = Path('config/taste_result_contract.json')
EXPECTED_CONTRACT = 'TASTE-SEMANTIC-RESULT-V5'


def load_active_producer_fence(contract_path=CONTRACT_PATH):
    contract = json.loads(Path(contract_path).read_text(encoding='utf-8'))
    if contract.get('contract') != EXPECTED_CONTRACT:
        raise SystemExit(
            f'Taste producer fence requires {EXPECTED_CONTRACT}; '
            f"found {contract.get('contract')!r}"
        )

    fence = contract.get('producer_fence')
    if not isinstance(fence, dict):
        raise SystemExit('Taste producer fence is missing from the canonical contract')

    producer_id = fence.get('active_producer_id')
    generation = fence.get('active_producer_generation')
    if not isinstance(producer_id, str) or not producer_id:
        raise SystemExit('Taste active producer id is missing or invalid')
    if isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
        raise SystemExit('Taste active producer generation is missing or invalid')

    return {
        'producer_id': producer_id,
        'producer_generation': generation,
    }


def validate_taste_producer_envelope(doc, *, source='<taste inbox>', fence=None):
    if not isinstance(doc, dict):
        raise SystemExit(f'{source} is not a JSON object')

    expected = fence or load_active_producer_fence()
    producer_id = doc.get('producer_id')
    generation = doc.get('producer_generation')

    if producer_id != expected['producer_id']:
        raise SystemExit(
            f'{source} rejected by Taste producer fence: producer_id '
            f'{producer_id!r} does not match active producer'
        )
    if (
        isinstance(generation, bool)
        or not isinstance(generation, int)
        or generation != expected['producer_generation']
    ):
        raise SystemExit(
            f'{source} rejected by Taste producer fence: producer_generation '
            f'{generation!r} does not match active generation'
        )

    return expected


def validate_taste_producer_file(path, *, fence=None):
    path = Path(path)
    try:
        doc = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f'{path} is not a readable Taste inbox JSON document: {exc}') from exc
    return validate_taste_producer_envelope(doc, source=str(path), fence=fence)
