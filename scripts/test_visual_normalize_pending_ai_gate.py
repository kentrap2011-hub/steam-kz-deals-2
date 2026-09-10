import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalize_visual_media_urls as normalizer


original_readiness = normalizer.readiness_builder.current_production_readiness
original_apply = normalizer.grounded_negative_visual.apply_to_current_visual
try:
    calls = []
    normalizer.readiness_builder.current_production_readiness = lambda: (None, {'status': 'degraded'})
    normalizer.grounded_negative_visual.apply_to_current_visual = lambda: calls.append('grounded')
    changed, stats, mode = normalizer.apply_grounded_negative_if_ready()
    assert changed is False
    assert mode == 'pending_ai_queue'
    assert calls == []
    assert stats['mapped_finding_count'] == 0

    normalizer.readiness_builder.current_production_readiness = lambda: ('cycle-key', {'status': 'complete'})
    normalizer.grounded_negative_visual.apply_to_current_visual = lambda: (
        True,
        {'mapped_finding_count': 3, 'visible_item_count': 2},
    )
    changed, stats, mode = normalizer.apply_grounded_negative_if_ready()
    assert changed is True
    assert mode == 'applied'
    assert stats['mapped_finding_count'] == 3
finally:
    normalizer.readiness_builder.current_production_readiness = original_readiness
    normalizer.grounded_negative_visual.apply_to_current_visual = original_apply

print('visual normalize pending-AI gate regression: ok')
