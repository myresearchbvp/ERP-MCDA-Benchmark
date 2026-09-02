from pathlib import Path
import csv
R=Path(__file__).resolve().parents[1]
def test_ne_not_zero():
 r={x['NP_ID']:x for x in csv.DictReader((R/'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv').open(encoding='utf-8-sig'))}; assert r['NP08']['Terminal_weight_perturbation_key_result']=='NE' and r['NP10']['Single_criterion_deletion_key_result']=='NE'
