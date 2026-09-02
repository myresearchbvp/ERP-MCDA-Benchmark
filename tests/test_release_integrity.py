from pathlib import Path
import csv, json
R=Path(__file__).resolve().parents[1]

def test_reader_scientific_scope_and_paths():
    text=(R/'README.md').read_text(encoding='utf-8')
    assert text.startswith('# ERP-MCDA Computational Reconstruction and Decision-Stability Benchmark')
    assert 'terminal-weight perturbation' in text
    assert 'single-criterion deletion' in text
    assert 'source-defined sensitivity analyses for NP04 and NP12' in text
    assert (R/'src/reference_implementations').is_dir()

def test_single_criterion_reference_note_semantics():
    text=(R/'results/reference/robustness/R2C/R2C_CASE_METHOD_NOTES.txt').read_text(encoding='utf-8')
    assert 'Total executed deletion-outcome rows=118' in text
    assert 'prespecified execution rule' in text

def test_colab_notebook_fails_closed_on_exact_commit():
    nb=json.loads((R/'notebooks/full_reproduction_colab.ipynb').read_text(encoding='utf-8'))
    text='\n'.join(''.join(c.get('source',[])) for c in nb.get('cells',[]))
    assert 'REPOSITORY_URL = "https://github.com/myresearchbvp/ERP-MCDA-Benchmark.git"' in text
    import re
    m=re.search(r'EXACT_COMMIT = \"([0-9a-f]{40})\"', text)
    assert m, 'Colab notebook must pin a 40-character Git commit'
    assert 'if not REPOSITORY_URL or not EXACT_COMMIT' in text
    assert '["git", "checkout", EXACT_COMMIT]' in text
    assert 'HEAD mismatch' in text

def test_scientific_checksum_scope():
    entries=[]
    for line in (R/'checksums.sha256').read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        digest, rel=line.split('  ',1)
        assert len(digest)==64 and (R/rel).is_file(), rel
        entries.append(rel)
    excluded={'README.md','LICENSE','THIRD_PARTY_DATA_AND_LICENSES.md','.gitignore'}
    excluded_prefixes=('LICENSES/','docs/','.github/','notebooks/','tests/')
    assert not any(rel in excluded or rel.startswith(excluded_prefixes) for rel in entries)
    assert any(rel.startswith('data/') for rel in entries)
    assert any(rel.startswith('results/reference/') for rel in entries)
    assert any(rel.startswith('src/') for rel in entries)

def test_applicability_status_semantics():
    with (R/'data/standardized/robustness/R2A/R2A_ROBUSTNESS_APPLICABILITY.csv').open(encoding='utf-8-sig',newline='') as f:
        r=list(csv.DictReader(f))
    assert 'robustness_applicability_summary' in r[0]
    with (R/'data/standardized/robustness/R2D/R2D_NATIVE_SENSITIVITY_APPLICABILITY.csv').open(encoding='utf-8-sig',newline='') as f:
        d=list(csv.DictReader(f))
    by={x['NP_ID']:x['execution_status'] for x in d}
    assert by['NP04']=='EXECUTED' and by['NP12']=='EXECUTED' and by['NP06']=='NE' and by['NP01']=='NOT_APPLICABLE'

def test_required_r2d_input_set():
    assert not (R/'data/standardized/robustness/R2D/INPUTS/R2A_ROBUSTNESS_APPLICABILITY.csv').exists()
    assert not (R/'data/standardized/robustness/R2D/INPUTS/R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv').exists()
