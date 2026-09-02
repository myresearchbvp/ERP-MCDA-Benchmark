from pathlib import Path
import csv
R=Path(__file__).resolve().parents[1]
def test_r2c_spec():
 r=list(csv.DictReader((R/'data/standardized/robustness/R2C/R2C_EXECUTION_SPEC.csv').open())); assert sum(x['applicability']=='APPLICABLE' for x in r)==118; assert sum(x['applicability']=='NE' for x in r)==47
def test_np04():
 r=list(csv.DictReader((R/'results/reference/robustness/R2D/R2D_NP04_SCENARIO_WEIGHT_VALIDATION.csv').open())); assert len(r)==720
