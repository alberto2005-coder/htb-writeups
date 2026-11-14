---
topic: MITRE ATT&CK mapping
tags: [threat-hunting, mitre, attck, detection, ttps, coverage]
---

# MITRE ATT&CK mapping

**English** | [🇪🇸 Español](mitre-attack-mapping.md)

## Concept

MITRE ATT&CK is a knowledge base of tactics and techniques observed in real attacks. Mapping a writeup, incident or detection rule to ATT&CK enables coverage comparison, telemetry prioritization and a common language for adversary behavior.

## When it applies

- Analyzing an actor or campaign.
- Designing detections and SIEM rules.
- Assessing telemetry gaps.
- Threat intelligence and DFIR reporting.

## Procedure

1. Describe the observable behavior, not the tool.
2. Find the matching tactic and technique.
3. Record the sub-technique and data source.
4. Check whether the organization has telemetry to detect it.
5. Document coverage and limitations.

```text
Action: Linux log deletion
Tactic: Defense Evasion (TA0005)
Technique: Indicator Removal (T1070)
Sub-technique: Clear Linux or Mac System Logs (T1070.002)
```

## Variants

- Mapping a group (Gxxxx) and its techniques.
- Mapping software (Sxxxx) to techniques.
- Reverse mapping: from a rule to the techniques it covers.
- Using ATT&CK Navigator for coverage layers.
- Mapping procedures to telemetry sources.

## Limitations

- ATT&CK describes behavior, not an IOC list.
- One technique can have many implementations.
- Mapping can be ambiguous without context.
- Rule coverage does not guarantee real detection.

## Mitigation and detection

- Validate each rule with real data and controlled tests.
- Prioritize techniques used by relevant actors.
- Document the data source and assumption.
- Review coverage periodically and after infrastructure changes.

## References

- <https://attack.mitre.org/>
- <https://mitre-attack.github.io/attack-navigator/>
- <https://attack.mitre.org/resources/attack-data-and-tools/>
- <https://www.cisa.gov/cyber-threat-intelligence>
