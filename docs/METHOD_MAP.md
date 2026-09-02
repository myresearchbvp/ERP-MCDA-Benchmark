# Method map

- **Native reconstruction:** per-case reference implementations with final documented source resolution. Canonical evaluable lineages are NP01–NP07, NP11, and NP12.
- **Terminal-weight perturbation (`R2B` machine key):** multiplicative factors `1 + epsilon`, with `epsilon ~ Uniform[-delta,+delta]`, renormalization, five perturbation magnitudes, 10,000 draws per applicable branch/configuration, and fixed seeds.
- **Single-criterion deletion (`R2C` machine key):** one-at-a-time criterion deletion with method-compatible recomputation; eight lineages are preflight-applicable, seven produce deletion results, with 118 applicable operations and 47 `NE` specification rows. NP11 remains preflight-applicable but execution-`NE`; no fallback solver is introduced.
- **Source-defined native sensitivity (`R2D` machine key):** NP04 has 30 Eq. (31) scenarios; NP06 is publication-reported only with source-defined reconstruction `NE`; NP12 uses q/v values in `{0, 0.25, 0.5, 0.75, 1}`.
