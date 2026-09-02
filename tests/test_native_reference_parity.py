from pathlib import Path
import csv
ROOT=Path(__file__).resolve().parents[1]
def test_final_native_lineages():
 r=list(csv.DictReader((ROOT/'results/reference/resolved/INTEGRATED_EVIDENCE_MATRIX.csv').open(encoding='utf-8-sig'))); a={x['NP_ID']:x for x in r}
 assert all(a[n]['Native_evaluability'] not in {'NOT_TERMINALLY_EVALUABLE','NOT_EVALUABLE_LITERAL_METHOD_NONFINITE','NOT_UNIQUELY_EVALUABLE_FROM_SUPPLIED_PUBLIC_SOURCE'} for n in ['NP01','NP02','NP03','NP04','NP05','NP06','NP07','NP11','NP12'])
