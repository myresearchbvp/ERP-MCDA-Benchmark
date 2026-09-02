from pathlib import Path
import csv, json, importlib.util
R=Path(__file__).resolve().parents[1]

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def notebook_text():
    nb=json.loads((R/'notebooks/full_reproduction_colab.ipynb').read_text(encoding='utf-8'))
    return '\n'.join(''.join(c.get('source',[])) for c in nb.get('cells',[]))

def test_runtime_reference_and_hosted_profile():
    m=load(R/'src/pipeline/colab_runtime.py','colab_runtime_test')
    assert m.CANONICAL_PYTHON==(3,13,5)
    src=(R/'src/pipeline/colab_runtime.py').read_text(encoding='utf-8')
    assert 'HOSTED_PYTHON_VERIFIED_COMPATIBILITY' in src
    assert 'hosted-colab' in src and 'PUBLICATION_PARITY.csv' in src and 'PARITY_REPORT.csv' in src

def test_np11_hosted_equivalence_is_scoped(tmp_path):
    m=load(R/'src/portable/native_runner.py','native_runner_test')
    ref=R/'results/reference/native/NP11/NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv'
    rows=list(csv.DictReader(ref.open(encoding='utf-8-sig',newline='')))
    rows[0]['total_global_weight']=f"{float(rows[0]['total_global_weight'])+5e-8:.12f}"
    got=tmp_path/ref.name
    with got.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['system','total_global_weight','rank']); w.writeheader(); w.writerows(rows)
    ok,note=m._np11_numeric_equivalent(got,ref); assert ok and 'max_abs=' in note
    rows[0]['rank']='1'; bad=tmp_path/'bad.csv'
    with bad.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['system','total_global_weight','rank']); w.writeheader(); w.writerows(rows)
    ok,_=m._np11_numeric_equivalent(bad,ref); assert not ok

def test_public_colab_uses_runtime_adapter_and_exact_commit():
    src=notebook_text()
    assert 'EXACT_COMMIT' in src and 'REPOSITORY_URL' in src
    assert 'prepare_runtime' in src and 'run_full_reproduction' in src
    assert 'REPRODUCTION_FAILURE' in src

def test_runtime_document_preserves_canonical_reference_and_scoped_gate():
    text=(R/'docs/COLAB_RUNTIME_COMPATIBILITY.md').read_text(encoding='utf-8')
    for x in ['Python 3.13.5','NumPy 2.3.5','SciPy 1.17.0','absolute tolerance `1e-6`']:
        assert x in text
