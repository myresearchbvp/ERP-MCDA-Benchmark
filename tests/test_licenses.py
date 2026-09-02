from pathlib import Path

R = Path(__file__).resolve().parents[1]

def test_dual_license_scope_present():
    mit = (R / 'LICENSE').read_text(encoding='utf-8')
    cc = (R / 'LICENSES/CC-BY-4.0.txt').read_text(encoding='utf-8')
    scope = (R / 'LICENSES/CONTENT_LICENSE_SCOPE.md').read_text(encoding='utf-8')
    assert mit.startswith('MIT License') and 'Permission is hereby granted' in mit
    assert 'Creative Commons Attribution 4.0 International Public License' in cc
    assert 'Source-derived factual records' in scope and 'Third-party materials' in scope
