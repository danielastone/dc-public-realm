# Pull-request merge rule

Squash merge only after all final-head checks succeed. Supply the passing head SHA as the expected head. If any check fails, diagnose the failing invariant rather than deleting the gate to obtain a green build.
