from pathlib import Path
import csv
R=Path(__file__).resolve().parents[1]
def rows(): return {x['NP_ID']:x for x in csv.DictReader((R/'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv').open(encoding='utf-8-sig'))}
def test_np10(): a=rows()['NP10']; assert (a['Final_D'],a['O'])==('D0','O3')
def test_np11(): a=rows()['NP11']; assert a['Single_criterion_deletion_preflight']=='APPLICABLE AT PREFLIGHT' and a['Single_criterion_deletion_execution_status'].startswith('NE UNDER')
