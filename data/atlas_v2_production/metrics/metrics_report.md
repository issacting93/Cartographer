# Atlas Graph Metrics Report

**Conversations Analyzed:** 968
**Total Constraints Tracked:** 2160
**Total Violations Detected:** 4848
**Total Repairs Attempted:** 87

## Overall Metrics

| Metric | Value |
|--------|-------|
| Drift Velocity (violations/turn) | 0.0891 |
| Agency Tax (repairs/violation) | 0.0269 |
| Constraint Half-Life (turns) | 4.0954 |
| Constraint Survival Rate | 0.3873 |
| Mode Violation Rate | 0.3804 |
| Repair Success Rate | 0.0555 |
| Mean Constraint Lifespan (turns) | 7.951 |
| Mode Entropy | 0.7762 |
| Move Coverage | 0.5786 |

## By Task Stability Class

| Stability Class | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|----------------|---|-----------|-----------|----------|----------|-----------|
| Agency Collapse | 26 | 0.088 | 0.0133 | 2.9167 | 0.3654 | 0.3865 |
| Constraint Drift | 470 | 0.1039 | 0.0348 | 3.5453 | 0.2956 | 0.3634 |
| No Constraints | 5 | 0.0507 | 0.0 | 5.0 | 0.3333 | 0.5429 |
| Task Maintained | 458 | 0.0737 | 0.0204 | 4.9314 | 0.4875 | 0.396 |
| Task Shift | 9 | 0.1294 | 0.0 | 4.0 | 0.1667 | 0.3658 |

## By Task Architecture

| Architecture | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|-------------|---|-----------|-----------|----------|----------|-----------|
| Analysis | 202 | 0.0882 | 0.0174 | 4.6021 | 0.3759 | 0.4038 |
| Generation | 346 | 0.1089 | 0.0405 | 3.6982 | 0.2985 | 0.2708 |
| Information Seeking | 252 | 0.0658 | 0.0176 | 4.2619 | 0.5371 | 0.5666 |
| Other | 2 | 0.0667 | 0.0 | 9.5 | 0.5 | 0.3833 |
| Planning | 46 | 0.1058 | 0.0181 | 3.3171 | 0.1851 | 0.3997 |
| Transformation | 120 | 0.0768 | 0.0272 | 4.5438 | 0.4233 | 0.2584 |

## By Constraint Hardness

| Hardness | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|----------|---|-----------|-----------|----------|----------|-----------|
| Flexible | 125 | 0.093 | 0.0591 | 4.3038 | 0.404 | 0.4337 |
| Mixed | 450 | 0.0857 | 0.0221 | 4.4208 | 0.4214 | 0.4067 |
| Strict | 393 | 0.0918 | 0.0222 | 3.7242 | 0.3429 | 0.3334 |
