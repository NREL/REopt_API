| no | name                    | uuid                                 | p/f  | note                               |
|----|-------------------------|--------------------------------------|------|------------------------------------|
| 1  | PV                      | 76168a37-a78b-4ef3-bdb8-a2f8b213430b | pass | timeStepScaling = 0.25             |
| 2  | PV2                     | 10c625b8-35b4-4b98-a01f-f4dc5732983c | pass | blended_annual_demand_charges      |
| 3  | PV3                     | ebfc3ee6-42d6-4a70-accb-15908e8ac2bf | fail | critical_load                      |
| 4  | wind                    | eda919d6-1481-4bf9-a531-a1b3397c8c67 | pass |                                    |
| 5  | storage                 | 2721ed09-7cdb-4d08-a690-28ca30eb6a6f | pass | (uncomment **Tech = [:UTIL1]**)    |
| 6  | PV + storage            | 8ff29780-4e1b-4aca-b079-1342ea21bde2 | pass |                                    |
| 7  | PV + storage + wind     | c8d51686-b991-43cd-bab7-68e03f8872d1 | pass |                                    |
| 8  | PV + wind               | b5e895b8-a851-49c0-9650-2072408d1b89 | pass |                                    |
| 9  | storage + wind          | 7605344c-964c-4e17-9c14-688d6e9fbfb6 | pass |                                    |
| 10 | tiered PV               | 5b75684a-232d-4e95-8bf1-3fcb47b07a46 | pass |                                    |
| 11 | tiered PV + BESS        | dc647e7a-be89-4044-ab40-e500a5f90e6b | pass |                                    |
| 12 | TOU PV                  | 02bd7144-c484-4e42-b7e4-9ea077bfbc34 | pass |                                    |
| 13 | TOU PV + BESS           | 6c15335f-4d77-4ade-a6f8-a4fd486488d1 | pass |                                    |
| 14 | PV + storage + MCA      | 5725f8a4-a3a1-4f5b-ac97-491718929be5 |      | modified dat files directly        |
| 15 | TOU PV + LBM            | dc52957d-a857-46cb-ad4c-989889c0592d |      | modified dat files directly        |
| 16 | wind + Monthly Demand   | 0cadae26-104a-4dad-a212-d0843a8cc4db |      | manually entered in rate (no URDB) |
