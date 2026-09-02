from pathlib import Path
import json, re
R=Path(__file__).resolve().parents[1]

def notebook_text():
    nb=json.loads((R/'notebooks/full_reproduction_colab.ipynb').read_text(encoding='utf-8'))
    return '\n'.join(''.join(c.get('source',[])) for c in nb.get('cells',[]))

def test_colab_requires_real_url_commit_and_verifies_head():
    text=notebook_text()
    assert 'REPOSITORY_URL = "https://github.com/myresearchbvp/ERP-MCDA-Benchmark.git"' in text
    m=re.search(r'EXACT_COMMIT = \"([0-9a-f]{40})\"', text)
    assert m, 'Colab notebook must pin a 40-character Git commit'
    assert 'if not REPOSITORY_URL or not EXACT_COMMIT' in text
    assert '["git", "checkout", EXACT_COMMIT]' in text
    assert '["git", "rev-parse", "HEAD"]' in text
    assert '["git", "rev-parse", EXACT_COMMIT]' in text
    assert 'HEAD mismatch' in text
    assert 'example.com' not in text

def test_reader_docs_and_release_metadata_are_present():
    for rel in ['README.md','THIRD_PARTY_DATA_AND_LICENSES.md','docs/METHOD_MAP.md','docs/SOURCE_PROVENANCE.md','docs/REFERENCE_IMPLEMENTATION_SCOPE.md']:
        assert (R/rel).is_file(),rel
