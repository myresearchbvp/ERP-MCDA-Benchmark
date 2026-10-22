# Reference implementation scope

`src/reference_implementations/` contains the scientific implementations required by the public reproduction route. They use the documented formulas, random seeds, solver settings and decision rules.

`results/reference/` contains scientific verification fixtures used by the pipeline and tests. These fixtures record the numeric values, ranks, winners, denominators, applicability states, `NE` statuses, and final classifications used for verification.

Adapters under `src/portable/` prepare the inputs and run these implementations in local and hosted environments.
