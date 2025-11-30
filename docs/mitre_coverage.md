# MITRE ATT&CK Coverage (Synthetic AI SOC)

This project includes simulated events and triage heuristics mapped to MITRE ATT&CK tactics/techniques. Use this as a quick reference and checklist as coverage grows.

## Current mappings (heuristic)

| Action | Tactics | Techniques |
| --- | --- | --- |
| login | Initial Access, Credential Access | T1078 (Valid Accounts) |
| login_failed | Credential Access | T1110 (Brute Force) |
| file_access / file_read | Exfiltration | T1048 (Exfiltration Over Alternative Protocol) |
| exfiltration | Exfiltration | T1041 (Exfiltration Over C2 Channel) |
| process_exec | Execution | T1059 (Command and Scripting Interpreter) |
| network_connect | Command and Control | T1071 (Application Layer Protocol) |
| lateral_movement | Lateral Movement | T1021 (Remote Services) |
| discovery_scan | Discovery | T1046 (Network Service Scanning), T1083 (File and Directory Discovery) |

These hints are attached to simulator events and surfaced via triage responses.

## How to extend
- Update `mitre/mapping.py` with new actions → tactics/techniques.
- Add simulated scenarios in `simulator/sim_generator.py` to emit new actions/tags.
- Triage prompts consume MITRE hints to improve categorization and recommended actions.

## Planned additions
- Lateral Movement (T1021)
- Persistence (T1053, T1505)
- Discovery (T1083, T1046)
- Privilege Escalation (T1068, T1078)

Contributions welcome—expand mappings and simulators to cover more ATT&CK techniques.***
