# Known NE cases and limitations

- NP08: terminally non-evaluable under documented source resolution because the formula-derived LP is non-unique and lacks a source tie-break.
- NP09: the literal published chain becomes non-finite at `ln(0)` with no documented source rule for replacing that operation.
- NP10: final D0/O3; Supplementary Tables S1–S6 and the operative direction mapping are unavailable, so no unique terminal baseline can be defined from the documented public source chain.
- NP11: all six criterion deletions have identified rankings in the post hoc analysis. Optimal LFPP weights and terminal score vectors remain nonunique. C6 has an unsuccessful SLSQP diagnostic; independent convex checks and rational/interval certificates establish its ranking. The original NP11 NE records describe nonexecution and are retained only under `historical/`. Source rounding does not establish score agreement; see `docs/NP11_CRITERION_DELETION.md`.
- NP06 single-criterion deletion analysis: NE because a reduced Choquet capacity is not defensibly reconstructible.

- NP04: In S16, the full-precision reconstruction placed SFT-5 above SFT-6, while the source workbook's rounded computational checkpoint yielded a tie; SFT-4 remained the winner.
- NP12: At all five parameter settings, the reconstructed Q values match Table 6 at its reported precision, and the rankings and acceptability conditions agree with Table 7. Table 7's printed advantage differences are inconsistent with Table 6; this discrepancy does not change the recommendation of A2.

Robustness conclusions are conditional on the two diagnostic designs, with NP11 deletion evaluated post hoc, and source-defined native analyses. No literature-wide prevalence or method-family robustness rate is supported.
