import argparse
import json

import build_progressive_pass2_work
import progressive_pass1
import progressive_pass2


def main():
    parser = argparse.ArgumentParser(
        description='Authorize one exact recovery-owned Deep identity for one fresh recovery attempt.'
    )
    parser.add_argument('--family-id', required=True)
    parser.add_argument('--reason', required=True, choices=sorted(progressive_pass2.RECOVERY_REASONS))
    parser.add_argument(
        '--condition-binding',
        default='',
        help='Concrete corrected-runtime/operator condition reference; optional only for material Dossier change.',
    )
    args = parser.parse_args()

    contexts = progressive_pass1.load_jsonl(progressive_pass1.PROGRESSIVE_CONTEXT)
    projection = progressive_pass2.load_json(progressive_pass1.TASTE_PROJECTION)
    queue_rows = progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    _generation, bindings, queue_by_family = progressive_pass1.current_bindings(
        contexts, projection, queue_rows
    )
    binding = bindings.get(args.family_id)
    if binding is None:
        raise SystemExit(f'current Deep identity not found for family_id={args.family_id}')

    queue_row = queue_by_family.get(args.family_id) or {}
    semantic_input = progressive_pass2._semantic_input(queue_row)
    dossier_binding = progressive_pass2.current_dossier_binding()
    dossier_record = progressive_pass2.canonical_dossier_loader(binding['appid'])
    if not isinstance(dossier_record, dict):
        raise SystemExit('current canonical Dossier is missing')

    if args.reason == 'materially_changed_canonically_accepted_dossier_or_evidence':
        condition = {
            'kind': 'material_dossier_or_evidence_change',
            'value': f"dossier_sha256:{dossier_record['content_sha256']}",
            'semantic_input': semantic_input,
        }
    else:
        value = args.condition_binding.strip()
        if not value:
            raise SystemExit('--condition-binding is required for defect/action recovery reasons')
        condition = {
            'kind': 'explicit_operator_condition',
            'value': value,
            'semantic_input': semantic_input,
        }

    state = progressive_pass2.load_state()
    updated, authorization = progressive_pass2.authorize_recovery(
        binding=binding,
        state_doc=state,
        dossier_record=dossier_record,
        current_binding=dossier_binding,
        recovery_reason=args.reason,
        recovery_condition_binding=condition,
    )

    progressive_pass2.STATE.write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )
    work = build_progressive_pass2_work.build_work_document()
    progressive_pass2.WORK.write_text(
        json.dumps(work, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    item = next(
        (
            row for row in work.get('items') or []
            if row.get('family_id') == args.family_id
            and row.get('work_mode') == 'recovery'
            and row.get('recovery_authorization_id') == authorization['recovery_authorization_id']
        ),
        None,
    )
    if item is None:
        raise SystemExit('recovery authorization did not produce exact current recovery work')

    print(
        'PROGRESSIVE_DEEP_RECOVERY_AUTHORIZATION=READY '
        f"family_id={args.family_id} "
        f"recovery_authorization_id={authorization['recovery_authorization_id']}"
    )


if __name__ == '__main__':
    main()
