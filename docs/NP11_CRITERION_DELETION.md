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

Winner retention is 5/6 = 0.8333; complete-ranking retention is 3/6 = 0.5000. All eight applicable benchmark lineages have evaluable deletion outcomes. The six rows are explicitly tagged `POST_HOC_NP11_EXTENSION`; they are not presented as part of the original 118-row execution. Current deletion outputs contain 124 rows and 41 current NE records. The original execution specification and result files are retained under the R2C `historical/` directories.

## Reproduce

The repository's quick command verifies NP11 input identities and replays its saved certificates. The full command also solves the baseline, all six deletion models and the local LFPP models with SLSQP, Clarabel and OSQP. To run only NP11:

```bash
python src/portable/np11_certified_deletion.py --output-dir reproduced_np11 --solve
```

The output contains the six outcomes, current solver diagnostics, source transcription, optimality/ranking verification and score-nonuniqueness checks. The existing source input CSVs remain unchanged. Their three SHA-256 identities are in `data/standardized/robustness/R2C/NP11_INPUT_IDENTITIES.json`.

`src/reference_implementations/robustness/NP11_LFPP_CERTIFICATION.py` implements the convex LFPP model and mathematical certificates. Saved rational primal/dual witnesses and LP dual bounds are in `results/reference/robustness/R2C/NP11/face_certificates.json`. Both modes check 13 QP certificates, 696 LP certificates and 33 feasible witnesses, then independently review the source constraints and composed ranking bounds with 180-digit interval arithmetic (1,032 LP checks including recursive rechecks). Every primary contrast is checked against the unchanged local ERP inputs. Rankings are reconstructed from the signs of the certified pairwise bounds, rather than copied from an expected ranking table. This establishes the decisions across the specified global optimum sets, conditional on the source transcription and correct arithmetic software; it is not formal verification of Python.

## Interpretation

Criterion weights and terminal score vectors are nonunique. The certified complete rankings are identified. SLSQP's C6 failure is retained; it is not treated as evidence that no decision can be identified. Current deletion-level rows leave the NP11 terminal-score-vector field empty because no unique vector is claimed; representative solver vectors and their statuses are available in the numerical output. Ordinal MARD and Kendall statistics are calculated from the certified rankings. Original case values and terminal-weight perturbation results remain unchanged.

The primary source is Panjavongroj and Phruksaphanrat, doi:10.3233/JIFS-221476. The corrected 15-page proof used for transcription has SHA-256 c6cb656abfd7c652f7754a8fdd3b36395870ce3ebdd6667399f128837ad62926. The source's full-precision optimizer and one C5/S4 rounding discrepancy remain unresolved, so score agreement is not claimed. No source article PDF is redistributed.
