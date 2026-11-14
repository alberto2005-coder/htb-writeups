---
sherlock: Bling Bling
category: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, neo4j, cypher, fraud, graph-analysis]
---

# Bling Bling — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal answers or real data.

## Scenario

During a Diwali discount campaign, a StoreD shop sees an abnormal volume of accounts. A Neo4j database is provided; find duplicate accounts, shared cards and reused addresses.

## Evidence

- `opsk-5.zip` with the Neo4j dump.
- `Account`, `CreditCard` nodes and registration relationships.
- No web logs or PCAP.

```bash
unzip opsk-5.zip
neo4j console
```

## Investigation

### 1. Inventory and triage

Import the dump and review labels and properties. Useful keys are `username`, `register_ip_address`, `address`, `created_at` and card number.

```cypher
MATCH (n) RETURN labels(n), count(*);
MATCH (n:Account) RETURN n LIMIT 5;
```

### 2. Timeline

Sort accounts by `created_at` and group by IP and physical address. A registration spike within hours is the abuse pattern.

```cypher
MATCH (a:Account)
RETURN a.register_ip_address, count(*) AS c
ORDER BY c DESC LIMIT 10;
```

### 3. Key artefact

The `HAS_CREDITCARD` relationship links one card to several accounts. That reuse is the main fraud evidence, together with the shared physical address.

## Conclusions

- The database holds over a thousand accounts.
- Several accounts share IP, address and card.
- The pattern suggests automated account creation to abuse discounts.
- Cypher queries make the analysis reproducible.

## Lessons

- Graph databases are ideal for relational fraud.
- IP alone is not enough: address and card confirm it.
- Documenting each query makes the report auditable.

## References

- <https://www.hackthebox.com/sherlocks/Bling%20Bling>
- <https://neo4j.com/docs/cypher-manual/current/>
- <https://attack.mitre.org/techniques/T1136/001/>
