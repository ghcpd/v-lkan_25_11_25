from kgeb.utils import merge_entities


def test_merge_conflict_detection():
    a = {"Person": [{"name": "John Doe", "age": 32, "position": "Researcher"}]}
    b = {"Person": [{"name": "John Doe", "age": 33, "position": "Researcher"}, {"name": "Jane Smith", "age": 28, "position": "Engineer"}]}
    merged, conflicts = merge_entities([a, b])
    # John Doe should be merged, and conflict should be recorded for age
    assert any(p.get('name') == 'John Doe' for p in merged['Person'])
    assert len(conflicts) >= 1
