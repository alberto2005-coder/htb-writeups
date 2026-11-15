---
topic: Ethereum — JSON-RPC and data in blocks
tags: [linux, ethereum, json-rpc, blockchain, osint]
---

# Ethereum — JSON-RPC and data in blocks

**English** | [🌐 Español](ethereum-jsonrpc-blockchain.md)

## Concept

An Ethereum node exposes JSON-RPC to query blocks and transactions. Transaction input is hex and may contain messages, credentials or paths. If the node is reachable, the blockchain becomes a public, permanent data channel that can be enumerated without authentication.

## When it applies

- Port `8545` or a JSON-RPC proxy is reachable.
- The application writes messages or configuration into transactions.
- A data channel independent from the main database is needed.

## Procedure

1. Confirm the JSON-RPC method and chain.
2. Query the latest block with full transactions.
3. Decode the `input` fields from hex to text.
4. Reuse the discovered data on the next service.

## Commands

```bash
curl -s -X POST http://<HOST>:8545 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",true],"id":1}'
# Decode a hex input
python3 -c "print(bytes.fromhex('<HEX>').decode(errors='ignore'))"
```

## Variants

- Walk historical blocks with `eth_getBlockByNumber`.
- Query transactions by hash with `eth_getTransactionByHash`.
- Use a public explorer if the node is not exposed.

## Limitations

- The node may restrict methods or require authentication.
- Data may be compressed or encrypted.
- Sync may not include recent blocks.

## Mitigation

- Do not store secrets on the blockchain.
- Restrict JSON-RPC to loopback and authenticate.
- Monitor block and transaction queries.

## Detection

- Bulk `eth_getBlockByNumber` queries.
- JSON-RPC access from unusual hosts.
- Sensitive data in the `input` field.

## References

- [0xdf — BlockBlock](https://0xdf.gitlab.io/2025/03/29/htb-blockblock.html)
- [Ethereum — JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- [CWE-200 — Exposure of Sensitive Information](https://cwe.mitre.org/data/definitions/200.html)
