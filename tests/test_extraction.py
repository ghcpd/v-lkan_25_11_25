import json
import os

def test_extractor_runs():
    os.system('python src/extract.py')
    assert os.path.exists('entities_output.json')
    assert os.path.exists('relations_output.json')
    e = json.load(open('entities_output.json'))
    assert 'Person' in e
