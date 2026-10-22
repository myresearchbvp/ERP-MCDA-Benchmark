# Method map

- **Native reconstruction:** per-case reference implementations with final documented source resolution. Canonical evaluable lineages are NP01–NP07, NP11, and NP12.
- **Terminal-weight perturbation (`R2B` machine key):** multiplicative factors `1 + epsilon`, with `epsilon ~ Uniform[-delta,+delta]`, renormalization, five perturbation magnitudes, 10,000 draws per applicable branch/configuration, and fixed seeds.
- **Single-criterion deletion (`R2C` machine key):** one-at-a-time criterion deletion with method-compatible recomputation; all eight applicable lineages produce evaluable results. The analysis contains 124 deletion outcomes, including six post hoc NP11 deletions, and 41 `NE` specification rows. NP11 recomputes LFPP criterion weights with M=1000 while retaining original local ERP weights; global optimum/ranking certificates establish the decisions despite nonunique weights and scores. The initial 118-row analysis is retained under `historical/`.
- **Source-defined native sensitivity (`R2D` machine key):** NP04 has 30 Eq. (31) scenarios; NP06 is publication-reported only with source-defined reconstruction `NE`; NP12 uses q/v values in `{0, 0.25, 0.5, 0.75, 1}`.
