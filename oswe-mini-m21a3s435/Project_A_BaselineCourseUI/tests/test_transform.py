import json
from src.transform import baseline_transform


def test_sanitize_script_in_hero():
    layout = {"hero": "<script>alert(1)</script>"}
    transformed, metrics = baseline_transform(layout)
    assert "&lt;script" in transformed['hero'] or "&lt;/script&gt;" in transformed['hero']


def test_metrics_basic():
    layout = {"hero": {"large": True, "image_height": 1000}, "sections": [{"type":"description","content":"x"*100}]}
    _, metrics = baseline_transform(layout)
    assert metrics['hero_large'] is True
    assert metrics['estimated_scroll'] > 100
