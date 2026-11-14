---
topic: Hardhat and unauthenticated JSON-RPC
tags: [blockchain, hardhat, json-rpc, ethereum, wallets, development]
---

# Hardhat and unauthenticated JSON-RPC

**English** | [🇪🇸 Español](hardhat-rpc.md)

## Concept

Hardhat Network exposes a local Ethereum node over JSON-RPC, usually on port 8545, without authentication. Test accounts are unlocked and the node can send transactions, change balances and reset state. If used with real wallets, anyone with access can drain them.

## When it applies

- Development environments reachable from the network.
- Ports 8545 or 8546 open.
- `eth_accounts` returning funded addresses.
- Contracts deployed on a local network.
- Apps signing transactions server-side.

## Procedure

1. Detect the port and `web3_clientVersion`.
2. List accounts with `eth_accounts`.
3. Query balances and contracts.
4. Send a transaction from an unlocked account.
5. Confirm the movement on-chain.

```bash
curl -s -X POST http://<IP>:8545 \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}'
```

## Variants

- `eth_sendTransaction` from an unlocked account.
- `hardhat_setBalance` to change balances.
- `hardhat_impersonateAccount` to impersonate an account.
- Contracts with functions lacking access control.
- Private keys in source or environment variables.

## Limitations

- The node must be reachable from the network.
- Accounts must be unlocked.
- Balances may be test funds with no real value.
- The network may require a fork or specific configuration.

## Mitigation and detection

- Do not expose the node beyond localhost.
- Use test networks without real funds.
- Authenticate RPC through a proxy and restrict methods.
- Alert on `eth_accounts`, `eth_sendTransaction` and unexpected balance changes.

## References

- <https://hardhat.org/hardhat-network/docs/overview>
- <https://ethereum.org/en/developers/docs/apis/json-rpc/>
- <https://attack.mitre.org/techniques/T1078/>
- <https://cwe.mitre.org/data/definitions/306.html>
