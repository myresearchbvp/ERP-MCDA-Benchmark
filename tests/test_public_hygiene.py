from pathlib import Path
import json, re, subprocess

R = Path(__file__).resolve().parents[1]

def test_no_cache_archive_or_third_party_source_binary_pollution():
    banned_suffix={'.zip','.pdf','.doc','.docx','.xls','.xlsx','.pyc','.pyo'}
    banned_dirs={'__pycache__','.pytest_cache'}
    if (R/'.git').exists():
        cp=subprocess.run(['git','-C',str(R),'ls-files','-z'],check=True,capture_output=True,text=True)
        paths=[Path(s) for s in cp.stdout.split('\0') if s]
    else:
        roots=['src','data','results','docs','notebooks','tests','LICENSES','.github']
        paths=[p.relative_to(R) for name in roots for p in (R/name).rglob('*')
               if p.is_file() and not any(part in banned_dirs for part in p.relative_to(R).parts)
               and p.suffix.lower() not in {'.pyc','.pyo'}]
        paths.extend(p.relative_to(R) for p in R.iterdir() if p.is_file()
                     and p.name not in {'erp_mcda_full_reproduction_result.zip'})
    bad=[p.as_posix() for p in paths if p.suffix.lower() in banned_suffix
         or any(part in banned_dirs for part in p.parts)]
    assert not bad,bad

def test_required_repository_metadata_and_single_notebook():
    notebooks=list((R/'notebooks').glob('*.ipynb'))
    assert [p.name for p in notebooks]==['full_reproduction_colab.ipynb']
    for rel in ['README.md','LICENSE','LICENSES/CC-BY-4.0.txt','LICENSES/CONTENT_LICENSE_SCOPE.md','.gitignore','.github/workflows/ci.yml','data/provenance/CASE_SOURCE_MAP.csv','data/provenance/SOURCE_MANIFEST_SHA256.csv']:
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
