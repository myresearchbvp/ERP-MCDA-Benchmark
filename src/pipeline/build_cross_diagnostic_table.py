"""Combine current perturbation, deletion and source-sensitivity results."""
from pathlib import Path
import csv

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def build(repo: Path, out: Path, result_root: Path | None = None):
    result_root = result_root or repo / "results/reference"
    perturbation = read(result_root / "robustness/R2B/R2B_TERMINAL_WEIGHT_PERTURBATION_SUMMARY.csv")
    deletion = {r["NP_ID"]: r for r in read(result_root / "robustness/R2C/R2C_CROSS_CASE_SUMMARY.csv")}
    native = {r["NP_ID"]: r for r in read(repo / "results/reference/robustness/R2D/R2D_NATIVE_SENSITIVITY_SUMMARY.csv")}
    rows=[]
    for npid, d in deletion.items():
        p=[r for r in perturbation if r["NP_ID"] == npid and float(r["delta"]) == 0.4]
        n=native[npid]
        descriptions=[]
        for r in p:
            key="baseline_recommendation_set_retention_frequency" if npid == "NP12" else "winner_retention_frequency"
            metric="recommendation_retention" if npid == "NP12" else "winner_retention"
            descriptions.append(f"{r['configuration_or_branch']}:{metric}@delta0.40={r[key]}")
        deletion_description = ("NE" if d["single_criterion_deletion_applicability"] == "NE" else
            f"retention_share={d['winner_or_recommendation_retention_share']}; critical={d['winner_or_recommendation_critical_deletions']}")
        note={"NP04":"NATIVE_EQ31_SCENARIOS_REPORTED_SEPARATELY_FROM_SINGLE_CRITERION_DELETION; TERMINAL_WEIGHT_PERTURBATION_NE",
              "NP06":"ROBUSTNESS_AUDITABILITY_LIMITED_BY_METHOD_SOURCE_STRUCTURE",
              "NP12":"THREE_DIAGNOSTIC_CLASSES_REPORTED_DESCRIPTIVELY_WITHOUT_POOLING"}.get(npid,"NO_ADDITIONAL_NATIVE_SENSITIVITY_DENOMINATOR")
        rows.append(dict(NP_ID=npid,
            terminal_weight_perturbation_availability="APPLICABLE" if p else "NE",
            terminal_weight_perturbation_result_descriptor=";".join(descriptions) if p else "NE",
            single_criterion_deletion_availability=d["single_criterion_deletion_applicability"],
            single_criterion_deletion_operation=d["operation_type"],
            single_criterion_deletion_result_descriptor=deletion_description,
            native_sensitivity_availability=n["native_sensitivity_disposition"],
            native_sensitivity_result=n["result_class"],
            qualitative_descriptive_note=note,
            pooling_rule="NO_POOLING_ACROSS_DIAGNOSTICS_OR_LINEAGES"))
    out.mkdir(parents=True,exist_ok=True)
    target=out/"R2D_CROSS_DIAGNOSTIC_DESCRIPTIVE_TABLE.csv"
    with target.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    return target
