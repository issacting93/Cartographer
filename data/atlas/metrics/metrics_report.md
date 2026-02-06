# Atlas Graph Metrics Report

**Conversations Analyzed:** 972
**Total Constraints Tracked:** 2173
**Total Violations Detected:** 4892
**Total Repairs Attempted:** 87

## Overall Metrics

| Metric | Value |
|--------|-------|
| Drift Velocity (violations/turn) | 0.0903 |
| Agency Tax (repairs/violation) | 0.0271 |
| Constraint Half-Life (turns) | 4.4791 |
| Constraint Survival Rate | 0.3814 |
| Mode Violation Rate | 0.3809 |
| Repair Success Rate | 0.0563 |
| Mean Constraint Lifespan (turns) | 7.9262 |
| Mode Entropy | 0.7773 |
| Move Coverage | 0.5785 |

## By Task Stability Class

| Stability Class | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|----------------|---|-----------|-----------|----------|----------|-----------|
| Agency Collapse | 26 | 0.0905 | 0.0133 | 3.0667 | 0.3462 | 0.3865 |
| Constraint Drift | 474 | 0.1036 | 0.035 | 3.8893 | 0.2943 | 0.3635 |
| No Constraints | 5 | 0.0507 | 0.0 | 4.3333 | 0.3333 | 0.5429 |
| Task Maintained | 458 | 0.0763 | 0.0205 | 5.4154 | 0.4784 | 0.3972 |
| Task Shift | 9 | 0.1294 | 0.0 | 4.4375 | 0.1667 | 0.362 |

## By Task Architecture

| Architecture | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|-------------|---|-----------|-----------|----------|----------|-----------|
| Analysis | 203 | 0.0883 | 0.0174 | 4.5039 | 0.3861 | 0.407 |
| Generation | 349 | 0.1092 | 0.0412 | 3.9798 | 0.298 | 0.2688 |
| Information Seeking | 252 | 0.068 | 0.0168 | 5.0945 | 0.5228 | 0.57 |
| Other | 2 | 0.0667 | 0.0 | 9.5 | 0.5 | 0.3833 |
| Planning | 46 | 0.1074 | 0.0181 | 3.7763 | 0.1699 | 0.3976 |
| Transformation | 120 | 0.0797 | 0.0279 | 5.391 | 0.3983 | 0.2591 |

## By Constraint Hardness

| Hardness | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|----------|---|-----------|-----------|----------|----------|-----------|
| Flexible | 125 | 0.0936 | 0.0578 | 4.4474 | 0.3973 | 0.4366 |
| Mixed | 452 | 0.085 | 0.0234 | 4.8993 | 0.4228 | 0.4076 |
| Strict | 395 | 0.0954 | 0.0216 | 4.101 | 0.329 | 0.3327 |
