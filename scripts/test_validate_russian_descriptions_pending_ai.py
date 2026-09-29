import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_russian_descriptions as validator


def main():
    original = validator.readiness_builder.current_production_readiness
    try:
        calls = []
        validator.readiness_builder.current_production_readiness = lambda: (
            calls.append('readiness') or (None, {'status': 'degraded'})
        )
        assert validator.semantic_validation_required(validator.CURRENT_VISUAL) is False
        assert calls == ['readiness']

        calls.clear()
        assert validator.semantic_validation_required(Path('/tmp/not-current.json')) is True
        assert calls == []

        validator.readiness_builder.current_production_readiness = lambda: (
            'cycle-key', {'status': 'complete'}
        )
        assert validator.semantic_validation_required(validator.CURRENT_VISUAL) is True

        with tempfile.TemporaryDirectory() as td:
            visual = Path(td) / 'visual.json'

            # Explicit unresolved state with no published summary is diagnostic,
            # not a release blocker.
            visual.write_text(json.dumps({'items': [{
                'id': 'game:1',
                'title': 'Needs Translation',
                'analysis_state': 'analyzed_fit',
                'summary': None,
                'description_status': 'needs_translation',
                'description_source_quality': 'non_ru',
            }]}), encoding='utf-8')
            validator.validate(visual)

            # The same unresolved status may never carry English/non-Russian text
            # as a visible summary.
            visual.write_text(json.dumps({'items': [{
                'id': 'game:2',
                'title': 'Masquerading English',
                'analysis_state': 'analyzed_fit',
                'summary': 'Explore the station and escape the creatures hunting you.',
                'description_status': 'needs_translation',
                'description_source_quality': 'non_ru',
            }]}), encoding='utf-8')
            try:
                validator.validate(visual)
            except SystemExit:
                pass
            else:
                raise AssertionError('non-Russian summary must remain release-blocking')

            visual.write_text(json.dumps({'items': [{
                'id': 'game:3',
                'title': 'Ready Russian',
                'analysis_state': 'analyzed_fit',
                'summary': 'Тактическое приключение с исследованием станции и поиском безопасного пути к спасению.',
                'description_status': 'ready_ru',
                'description_source_quality': 'good_ru',
            }]}), encoding='utf-8')
            validator.validate(visual)
    finally:
        validator.readiness_builder.current_production_readiness = original

    print('pending-AI Russian description gate regression: ok')


if __name__ == '__main__':
    main()
