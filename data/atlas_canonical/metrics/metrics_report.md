# Atlas Graph Metrics Report

**Conversations Analyzed:** 744
**Total Constraints Tracked:** 376
**Total Violations Detected:** 3188
**Total Repairs Attempted:** 54

## Overall Metrics

| Metric | Value |
|--------|-------|
| Drift Velocity (violations/turn) | 0.0211 |
| Agency Tax (repairs/violation) | 0.0201 |
| Constraint Half-Life (turns) | 2.4911 |
| Constraint Survival Rate | 0.0616 |
| Mode Violation Rate | 0.4202 |
| Repair Success Rate | 0.0011 |
| Mean Constraint Lifespan (turns) | 1.3022 |
| Mode Entropy | 0.8189 |
| Move Coverage | 0.5554 |

## By Task Stability Class

| Stability Class | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|----------------|---|-----------|-----------|----------|----------|-----------|
| Agency Collapse | 10 | 0.007 | 0.0 | 2.0 | 0.05 | 0.2413 |
| Constraint Drift | 147 | 0.0746 | 0.026 | 2.4009 | 0.2129 | 0.3337 |
| No Constraints | 276 | 0.0 | 0.0148 | None | 0.0 | 0.4714 |
| Task Maintained | 304 | 0.0151 | 0.0199 | 2.5918 | 0.044 | 0.4249 |
| Task Shift | 7 | 0.0071 | 0.1429 | 9.0 | 0.0952 | 0.2643 |

## By Task Architecture

| Architecture | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|-------------|---|-----------|-----------|----------|----------|-----------|
| Analysis | 185 | 0.0162 | 0.0198 | 1.7576 | 0.0369 | 0.4834 |
| Discussion | 1 | 0.0 | 0.25 | None | 0.0 | 0.6667 |
| Generation | 255 | 0.0317 | 0.0279 | 2.625 | 0.0949 | 0.3212 |
| Information Seeking | 200 | 0.0086 | 0.0084 | 2.5909 | 0.0227 | 0.5654 |
| Other | 9 | 0.0 | 0.0 | None | 0.0 | 0.3139 |
| Planning | 27 | 0.053 | 0.0037 | 2.0 | 0.0247 | 0.3945 |
| Transformation | 67 | 0.0215 | 0.0323 | 3.4706 | 0.143 | 0.2096 |

## By Constraint Hardness

| Hardness | N | Drift Vel. | Agency Tax | Half-Life | Survival | Mode Viol. |
|----------|---|-----------|-----------|----------|----------|-----------|
| Flexible | 154 | 0.0057 | 0.0293 | 2.75 | 0.0162 | 0.4396 |
| Mixed | 46 | 0.0871 | 0.0242 | 3.0476 | 0.2851 | 0.2774 |
| Strict | 544 | 0.0199 | 0.0172 | 2.2754 | 0.0555 | 0.4268 |
