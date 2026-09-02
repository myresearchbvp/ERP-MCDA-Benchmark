from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]

def test_citation_cff_required_metadata():
    text=(R/'CITATION.cff').read_text(encoding='utf-8')
    assert 'cff-version: 1.2.0' in text
    assert 'ERP-MCDA Computational Reconstruction and Decision-Stability Benchmark' in text
    for oid in ['0000-0002-7240-6187','0000-0001-9285-9178','0009-0005-1062-3396','0009-0006-4106-781X']:
        assert oid in text
    assert 'paul.bresfelean@econ.ubbcluj.ro' in text
    assert not re.search(r'github\.com/|zenodo|doi:\s*10\.',text,re.I)

def test_dual_license_scope_present():
    mit=(R/'LICENSE').read_text(encoding='utf-8')
    cc=(R/'LICENSES/CC-BY-4.0.txt').read_text(encoding='utf-8')
    scope=(R/'LICENSES/CONTENT_LICENSE_SCOPE.md').read_text(encoding='utf-8')
    assert mit.startswith('MIT License') and 'Permission is hereby granted' in mit
    assert 'Creative Commons Attribution 4.0 International Public License' in cc
    assert 'Source-derived factual records' in scope and 'Third-party materials' in scope
