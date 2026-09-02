#!/usr/bin/env python3
"""Offline adapter for the prespecified single-criterion deletion reproduction.

The adapter stages the documented execution specification and delegates all scientific
computations to the execution-only reference implementation without changing formulas,
solver settings, or decision rules.
"""
from __future__ import annotations
from pathlib import Path
from types import SimpleNamespace
import importlib.util, shutil

def load(path:Path):
    spec=importlib.util.spec_from_file_location("r2c_reference",path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def reproduce(repo:Path,out:Path):
    code=repo/"src/reference_implementations/robustness/R2C_SINGLE_CRITERION_DELETION.py"
    m=load(code)
    spec_src=repo/"data/standardized/robustness/R2C/R2C_EXECUTION_SPEC.csv"
    out.mkdir(parents=True,exist_ok=True); shutil.copy2(spec_src,out/"R2C_EXECUTION_SPEC.csv")
    rt=repo/"data/standardized/runtime"
    args=SimpleNamespace(r1a=rt/"R1A",r1b=rt/"R1B",r1c=rt/"R1C",r1d=rt/"R1D",
                         r2a=repo/"data/standardized/robustness/R2A",r2b=rt/"R2B",out=out)
    inp=m.Inputs(args.r1a,args.r1b,args.r1c,args.r1d,args.r2a,args.r2b)
    m.execute_deletions(args,inp,out)
    return out
