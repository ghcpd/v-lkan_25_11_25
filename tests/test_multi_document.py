from pathlib import Path
from kgeb.cli import _read_documents


def test_multi_document_reading(tmp_path):
    doc1 = tmp_path / "a.txt"
    doc2 = tmp_path / "b.txt"
    doc1.write_text("Alice, age 30, works at FooCorp as a Engineer.")
    doc2.write_text("Bob, age 25, works at BarCorp as an Analyst.")
    text = _read_documents([str(doc1), str(doc2)])
    assert "Alice" in text and "Bob" in text


def test_multi_document_directory(tmp_path):
    d = tmp_path / "docs"
    d.mkdir()
    (d / "x.txt").write_text("Carol, age 40, works at BazCorp as a Manager.")
    combined = _read_documents([str(d)])
    assert "Carol" in combined
