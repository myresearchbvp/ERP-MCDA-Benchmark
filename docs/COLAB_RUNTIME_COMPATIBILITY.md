# Colab runtime compatibility

The canonical deterministic reference remains unchanged: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, and pytest 9.0.2. `environment-lock.yml` records the Python reference and `requirements-lock.txt` records the exact direct Python dependency versions.

Google Colab controls both the host image and the CPU/BLAS execution backend. The notebooks therefore use `src/pipeline/colab_runtime.py` to create an isolated runtime and then execute FULL reproduction through the explicit `hosted-colab` parity profile.

## Why a hosted profile is required

The reference NP11 reconstruction uses SciPy SLSQP for the LFPP optimization and prints weights to 12 decimal places. The documented ranking and winner are stable, but lower-order floating digits can vary with the CPU/OpenBLAS backend even with identical Python, NumPy, and SciPy versions. This was reproduced locally by changing only OpenBLAS execution settings: the reference script returned the same system order, ranks, winner, and scientific interpretation while lower-order printed weights changed.

A second portability-only effect was observed in the R2C deletion-level output under an intentionally different OpenBLAS architecture: three `terminal_score_vector` tokens changed only in the final printed decimal place, while every decision/status field and every summary object remained identical.

The canonical reference route remains byte-strict. The hosted Colab profile is narrowly different only for hardware-sensitive printed numeric fields:

- `NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv`: identical schema/order/system IDs/ranks/winner; finite numeric values within absolute tolerance `1e-6`.
- `NP11_CALCULATED_INTERMEDIATES.csv`: identical schema/order/stage/basis/item/metric labels; finite numeric values within absolute tolerance `1e-6`.
- `R2C_DELETION_LEVEL_RESULTS.csv`: every field is exact except parsed numeric values inside `terminal_score_vector`, which must remain within absolute tolerance `1e-9`; all winner/recommendation/status/order fields remain exact.
- `NP11_RECONSTRUCTION_VALIDATION.txt` remains exact where hardware-independent.

Every other native, robustness, source-resolution, publication, denominator, checksum, and source-reference consistency check remains unchanged and strict. A mismatch outside these exact fields is a hard failure.

These are runtime-portability equivalence checks, not scientific fallbacks. They do not alter reference scripts, solvers, objectives, bounds, tolerances, initialization, formulas, seeds, benchmark membership, denominators, NE statuses, documented reference files, or publication values.

## Runtime selection

1. If the host is already Python 3.13.5, create a clean virtual environment and install `requirements-lock.txt`.
2. Otherwise, first provision an isolated Python 3.13.5 environment and install `requirements-lock.txt`.
3. If platform or network policy prevents canonical-Python provisioning, create an isolated environment from the hosted interpreter and install the same exact dependency lock.
4. Execute FULL reproduction with `--runtime-profile hosted-colab` so the fail-closed hardware-portability equivalence checks are available only where documented above.

The runtime adapter streams subprocess output. On failure it prints the return code, available `PARITY_REPORT.csv` non-PASS rows, expected and observed hashes when available, and the retained pipeline output tail. A mismatch beyond a declared tolerance, any rank/winner/status change, or any mismatch elsewhere remains a hard failure.

A live hosted Colab execution is a separate runtime validation step. Local simulation of the hosted profile and static notebook checks do not by themselves constitute a live Colab execution.
