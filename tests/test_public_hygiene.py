from pathlib import Path
import json, re

R = Path(__file__).resolve().parents[1]

def test_no_cache_archive_or_third_party_source_binary_pollution():
    bad=[]
    banned_suffix={'.zip','.pdf','.doc','.docx','.xls','.xlsx','.pyc','.pyo'}
    banned_dirs={'__pycache__','.pytest_cache'}
    for p in R.rglob('*'):
        rel=p.relative_to(R)
        if any(part in banned_dirs for part in rel.parts): bad.append(rel.as_posix())
        if p.is_file() and p.suffix.lower() in banned_suffix: bad.append(rel.as_posix())
    assert not bad,bad

def test_required_repository_metadata_and_single_notebook():
    notebooks=list((R/'notebooks').glob('*.ipynb'))
    assert [p.name for p in notebooks]==['full_reproduction_colab.ipynb']
    for rel in ['README.md','CITATION.cff','LICENSE','LICENSES/CC-BY-4.0.txt','LICENSES/CONTENT_LICENSE_SCOPE.md','.gitignore','.github/workflows/ci.yml','data/provenance/CASE_SOURCE_MAP.csv','data/provenance/SOURCE_MANIFEST_SHA256.csv']:
        assert (R/rel).is_file(), rel

def test_repo_relative_scientific_locators_resolve():
    text_suffixes={'.py','.md','.txt','.csv','.yml','.yaml','.toml','.cff','.ipynb',''}
    pat=re.compile(r'(?<![A-Za-z0-9_./])((?:data|results|src)/[A-Za-z0-9_./-]+\.(?:csv(?:\.gz)?|txt|py|md))')
    dead=[]
    for p in R.rglob('*'):
        if not p.is_file() or p.name=='checksums.sha256' or p.parts[-2:-1]==('tests',) or p.suffix.lower() not in text_suffixes: continue
        try: text=p.read_text(encoding='utf-8')
        except UnicodeDecodeError: continue
        for m in pat.finditer(text):
            token=m.group(1).rstrip('.,;:)')
            if 'NPxx_' in token: continue
            if not (R/token).is_file(): dead.append((p.relative_to(R).as_posix(),token))
    assert not dead,dead[:30]
