# Reference implementation scope

`src/reference_implementations/` contains the scientific implementations required by the public reproduction route. They implement the documented computational formulas, seeds, solver settings, and decision rules required for reproduction.

`results/reference/` contains scientific verification fixtures used by the pipeline and tests. These fixtures record the numeric values, ranks, winners, denominators, applicability states, `NE` statuses, and final classifications used for verification.

Portable adapters under `src/portable/` stage repository data and handle public-runtime constraints; they do not substitute alternative scientific methods.
