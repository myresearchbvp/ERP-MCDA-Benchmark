# NP11 criterion deletion

The post hoc analysis removes each criterion C1–C6, recomputes the remaining LFPP criterion weights with M=1000 and holds the original local ERP alternative weights fixed. DEMATEL is excluded. The baseline ranking is S4 > S3 > S1 > S2.

| Removed criterion | Complete ranking |
| --- | --- |
| C1 | S4 > S3 > S1 > S2 |
| C2 | S4 > S1 > S3 > S2 |
| C3 | S4 > S3 > S1 > S2 |
| C4 | S4 > S3 > S2 > S1 |
| C5 | S4 > S3 > S1 > S2 |
| C6 | S3 > S1 > S2 > S4 |

Winner retention is 5/6 = 0.8333; complete-ranking retention is 3/6 = 0.5000. All eight applicable benchmark lineages have evaluable deletion outcomes. Current results comprise 124 deletion outcomes and 41 `NE` specification records. The six NP11 outcomes carry the `POST_HOC_NP11_EXTENSION` flag; earlier execution records are retained under `R2C/historical/`.

## Reproduce

The repository's quick command verifies NP11 input identities and replays its saved certificates. The full command also solves the baseline, all six deletion models and the local LFPP models with SLSQP, Clarabel and OSQP. To run only NP11:

```bash
python src/portable/np11_certified_deletion.py --output-dir reproduced_np11 --solve
```

The output contains the six outcomes, solver diagnostics, source transcription, optimality and ranking checks, and score-nonuniqueness results. Input hashes are recorded in `data/standardized/robustness/R2C/NP11_INPUT_IDENTITIES.json`.

`src/reference_implementations/robustness/NP11_LFPP_CERTIFICATION.py` implements the convex LFPP model and mathematical certificates. Saved rational primal/dual witnesses and LP dual bounds are in `results/reference/robustness/R2C/NP11/face_certificates.json`. Both modes check 13 QP certificates, 696 LP certificates and 33 feasible witnesses, then independently review the source constraints and composed ranking bounds with 180-digit interval arithmetic (1,032 LP checks including recursive rechecks). Each primary contrast uses the fixed local ERP weights. Rankings follow from the signs of the certified pairwise bounds over the specified global optimum sets. These results are conditional on accurate source transcription.

## Interpretation

Criterion weights and terminal score vectors are nonunique. The certified complete rankings are identified. For C6, SLSQP does not report convergence, but the convex certificates establish the complete ranking. The NP11 `terminal_score_vector` field is empty because the optimum score vector is nonunique. Representative solver vectors and convergence statuses are included in the numerical output. MARD and Kendall statistics are calculated from the certified rankings.

The primary source is Panjavongroj and Phruksaphanrat, doi:10.3233/JIFS-221476. The source values were transcribed from the corrected 15-page article proof (SHA-256: c6cb656abfd7c652f7754a8fdd3b36395870ce3ebdd6667399f128837ad62926). The source's full-precision optimizer and one C5/S4 rounding discrepancy remain unresolved, so score agreement is not claimed. No source article PDF is redistributed.
