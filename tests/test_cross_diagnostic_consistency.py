from pathlib import Path
import csv, importlib.util, sys

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from pipeline.build_cross_diagnostic_table import build

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def test_all_deletion_states_match_current_results(tmp_path):
    got=read(build(R,tmp_path))
    deletion={r['NP_ID']:r for r in read(R/'results/reference/robustness/R2C/R2C_CROSS_CASE_SUMMARY.csv')}
    assert len(got)==len(deletion)==12
    for r in got:
        assert r['single_criterion_deletion_availability']==deletion[r['NP_ID']]['single_criterion_deletion_applicability']
    np11=next(r for r in got if r['NP_ID']=='NP11')
    assert np11['single_criterion_deletion_availability']=='APPLICABLE'
    assert np11['single_criterion_deletion_result_descriptor']=='retention_share=0.833333333333333; critical=1'
    assert (tmp_path/'R2D_CROSS_DIAGNOSTIC_DESCRIPTIVE_TABLE.csv').read_bytes()==(R/'results/reference/robustness/R2D/R2D_CROSS_DIAGNOSTIC_DESCRIPTIVE_TABLE.csv').read_bytes()
