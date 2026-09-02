#!/usr/bin/env python3
"""Offline adapter for source-defined native sensitivity.

Primary NP04 Eq.(31) and NP12 q/v calculations are recomputed by the reference implementation.
The third-party NP04 workbook is not redistributed. Its documented source-audit records are
therefore used as repository standardized research records rather than re-extracted.
"""
from __future__ import annotations
from pathlib import Path
import shutil, subprocess, sys

def reproduce_primary(repo:Path,out:Path):
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    work=out/'_work'
    work.mkdir()
    shutil.copy2(repo/'src/reference_implementations/robustness/R2D_SOURCE_DEFINED_SENSITIVITY.py',work/'R2D_SOURCE_DEFINED_SENSITIVITY.py')
    for n in ['R2D_EXECUTION_SPEC.csv','R2D_NATIVE_SENSITIVITY_APPLICABILITY.csv']:
        shutil.copy2(repo/'data/standardized/robustness/R2D'/n,work/n)
    shutil.copytree(repo/'data/standardized/robustness/R2D/INPUTS',work/'INPUTS')
    cp=subprocess.run([sys.executable,str(work/'R2D_SOURCE_DEFINED_SENSITIVITY.py')],cwd=work,text=True,capture_output=True)
    if cp.returncode!=0:
        raise RuntimeError(f'R2D source-defined sensitivity subprocess failed with exit={cp.returncode}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}')
    produced=[
        'R2D_NP04_30_SCENARIO_RESULTS.csv',
        'R2D_NP04_CRITERION_MAPPING.csv',
        'R2D_NP04_PRIMARY_EQ31_SCENARIO_WEIGHTS.csv',
        'R2D_NP04_SCENARIO_WEIGHT_VALIDATION.csv',
        'R2D_NP12_Q_SWEEP_RESULTS.csv',
    ]
    for name in produced:
        src=work/name
        if not src.exists(): raise FileNotFoundError(f'R2D source-defined sensitivity output missing: {name}')
        shutil.copy2(src,out/name)
    shutil.rmtree(work)
    return out
