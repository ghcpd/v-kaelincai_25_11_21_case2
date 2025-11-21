from src.transform import enhanced_transform


def test_pinned_info_and_collapsibles():
    layout = {"hero": {"title":"Course","large": True}, "sections": [{"type":"syllabus","content":["A","B"]}] , "cta": {"label":"Enroll","price":"$50"}}
    transformed, metrics = enhanced_transform(layout)
    assert transformed['ui']['info_card_pinned'] is True
    assert metrics['collapsibles'] >= 1 or metrics['total_sections'] >= 1


def test_malformed_sections_safefallback():
    layout = {"hero":"h","sections": "malformed"}
    transformed, metrics = enhanced_transform(layout)
    assert transformed['ui'].get('safe_fallback_sections', False) or isinstance(transformed.get('sections'), list)
