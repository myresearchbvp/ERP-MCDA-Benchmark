from pathlib import Path
import csv, importlib.util
import pytest

R=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('token',['nan','inf','-inf'])
def test_nonfinite_r2c_score_is_rejected(tmp_path,token):
    spec=importlib.util.spec_from_file_location('reproduce_nonfinite',R/'src/pipeline/reproduce_all.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    reference=R/'results/reference/robustness/R2C/R2C_DELETION_LEVEL_RESULTS.csv'
    rows=module.csv_rows(reference)
    first=rows[0]['terminal_score_vector'].split(';')[0]
    rows[0]['terminal_score_vector']=rows[0]['terminal_score_vector'].replace(first,first.split('=')[0]+'='+token,1)
    target=tmp_path/'scores.csv'
    with target.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    ok,note=module._compare_r2c_deletion_hosted(target,reference)
    assert not ok and 'non-finite' in note
