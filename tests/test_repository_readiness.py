from pathlib import Path
import json, re
R=Path(__file__).resolve().parents[1]

def notebook_text():
    nb=json.loads((R/'notebooks/full_reproduction_colab.ipynb').read_text(encoding='utf-8'))
    return '\n'.join(''.join(c.get('source',[])) for c in nb.get('cells',[]))

def test_colab_pins_scientific_manifest_and_records_head():
    text=notebook_text()
    assert 'REPOSITORY_URL = "https://github.com/myresearchbvp/ERP-MCDA-Benchmark.git"' in text
    m=re.search(r'EXPECTED_MANIFEST_SHA256 = \"([0-9a-f]{64})\"', text)
    assert m, 'Colab notebook must pin the 64-character scientific manifest SHA-256'
    assert 'if not REPOSITORY_URL or not REVISION or not EXPECTED_MANIFEST_SHA256' in text
    assert '["git", "checkout", REVISION]' in text
    assert '["git", "rev-parse", "HEAD"]' in text
    assert '["git", "rev-parse", REVISION]' in text
    assert 'HEAD mismatch' in text
    assert 'example.com' not in text

def test_reader_docs_and_release_metadata_are_present():
    for rel in ['README.md','THIRD_PARTY_DATA_AND_LICENSES.md','docs/METHOD_MAP.md','docs/SOURCE_PROVENANCE.md','docs/REFERENCE_IMPLEMENTATION_SCOPE.md']:
        assert (R/rel).is_file(),rel
