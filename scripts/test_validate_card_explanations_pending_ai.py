import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_card_explanations as validator


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
    finally:
        validator.readiness_builder.current_production_readiness = original

    print('pending-AI card validation gate regression: ok')


if __name__ == '__main__':
    main()
