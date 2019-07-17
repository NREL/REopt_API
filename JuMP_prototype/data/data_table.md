| no | name                | uuid                                 |                                      | note                                                          |
|----|---------------------|--------------------------------------|--------------------------------------|---------------------------------------------------------------|
| 1  | PV                  | 76168a37-a78b-4ef3-bdb8-a2f8b213430b | pass                                 | timeStepScaling = 0.25                                        |
| 2  | PV2                 | 10c625b8-35b4-4b98-a01f-f4dc5732983c | pass                                 | blended_annual_demand_charges                                 |
| 3  | PV3                 | ebfc3ee6-42d6-4a70-accb-15908e8ac2bf | pass                                 | critical_load                                                 |
| 4  | wind                | eda919d6-1481-4bf9-a531-a1b3397c8c67 | pass                                 |                                                               |
| 5  | storage             | 2721ed09-7cdb-4d08-a690-28ca30eb6a6f | pass (uncomment **Tech = [:UTIL1]**) | ERROR: LoadError: LoadError: UndefVarError: Tech not defined. |
| 6  | PV + storage        | 8ff29780-4e1b-4aca-b079-1342ea21bde2 | not converged                        | B&B tree search gap not converged... 52.15% after 15 hrs      |
| 7  | PV + storage + wind | c8d51686-b991-43cd-bab7-68e03f8872d1 | not converged                        | B&B tree search gap not converged... 79.67% after 1.5 hrs      |
| 8  | PV + wind           | b5e895b8-a851-49c0-9650-2072408d1b89 | pass                                 |                                                               |
| 9  | storage + wind      | 7605344c-964c-4e17-9c14-688d6e9fbfb6 | not converged                        | B&B tree search gap not converged... 44.83% after 1.5 hrs      |
| 10 | gen                 |                                      |                                      |                                                               |
| 11 | PV + gen            |                                      |                                      |                                                               |
|    |                     |                                      |                                      |                                                               |