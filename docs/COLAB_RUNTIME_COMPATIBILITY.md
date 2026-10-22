# Colab runtime compatibility

The reference environment uses Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0 and pytest 9.0.2. NP11 also requires Clarabel 0.11.1, OSQP 1.1.3, SymPy 1.14.0 and mpmath 1.3.0. The versions are recorded in `environment-lock.yml` and `requirements-lock.txt`.

Google Colab controls the host interpreter and CPU/BLAS backend. The notebook uses `src/pipeline/colab_runtime.py` to create an isolated environment and runs the analysis with `--runtime-profile hosted-colab`.

## Numerical comparison

SLSQP's printed NP11 weights can differ in their final decimal places across CPU/OpenBLAS backends. The same effect can occur in printed R2C terminal scores. The `hosted-colab` profile permits these differences within the following bounds:

- `NP11_COMPUTED_OUTPUTS_PRECOMPARISON.csv`: absolute tolerance `1e-6` for finite numeric values; schema, row order, system IDs, ranks and winner must match exactly.
- `NP11_CALCULATED_INTERMEDIATES.csv`: absolute tolerance `1e-6` for finite numeric values; schema, row order and stage, basis, item and metric labels must match exactly.
- `R2C_DELETION_LEVEL_RESULTS.csv`, including the historical file: absolute tolerance `1e-9` for finite numeric values in `terminal_score_vector`; every other field must match exactly.

All other output comparisons are exact. The `strict-byte` profile requires byte-identical files throughout. Mathematical certificate checks use exact rational or outward-rounded interval arithmetic, independently of these floating-point tolerances.

## Runtime selection

The adapter creates a Python 3.13.5 environment when available. If platform or network restrictions prevent this, it uses the hosted interpreter with the same pinned dependencies. A failed comparison stops execution and reports the affected rows and diagnostics.

The notebook checks the checksum manifest before execution and records the resolved Git commit. It is excluded from the manifest because it stores the manifest's own hash.

The full run also reruns three NP11 solvers. Both full and quick runs verify the saved rational/interval certificates, including their input identities, pairwise signs and rankings. `PARITY_REPORT.csv` and `PUBLICATION_PARITY.csv` record the comparison results.
