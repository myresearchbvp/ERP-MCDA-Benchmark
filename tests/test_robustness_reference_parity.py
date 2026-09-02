from pathlib import Path
import csv,gzip
R=Path(__file__).resolve().parents[1]
def test_r2b_rows():
 with gzip.open(R/'results/reference/robustness/R2B/R2B_DRAW_LEVEL_METRICS.csv.gz','rt',encoding='utf-8',newline='') as f: assert sum(1 for _ in f)-1==650000
def test_r2c_counts():
 rows=list(csv.DictReader((R/'results/reference/robustness/R2C/R2C_DELETION_LEVEL_RESULTS.csv').open())); assert len(rows)==118
