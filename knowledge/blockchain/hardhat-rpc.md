---
topic: Hardhat y JSON-RPC sin autenticación
tags: [blockchain, hardhat, json-rpc, ethereum, wallets, development]
---

# Hardhat y JSON-RPC sin autenticación

[🌐 English](hardhat-rpc.en.md) | **Español**

## Concept

Hardhat Network expone un nodo Ethereum local por JSON-RPC, normalmente en el puerto 8545, sin autenticación. Las cuentas de prueba están desbloqueadas y el nodo permite enviar transacciones, modificar saldos y reiniciar el estado. Si se usa con wallets reales, cualquiera con acceso puede vaciarlas.

## Cuándo aplica

- Entornos de desarrollo accesibles desde la red.
- Puertos 8545 o 8546 abiertos.
- `eth_accounts` que devuelve direcciones con saldo.
- Contratos desplegados en una red local.
- Aplicaciones que firman transacciones en el servidor.

## Procedimiento

1. Detectar el puerto y el `web3_clientVersion`.
2. Listar cuentas con `eth_accounts`.
3. Consultar saldos y contratos.
4. Enviar una transacción desde una cuenta desbloqueada.
5. Confirmar el movimiento en la cadena.

```bash
curl -s -X POST http://<IP>:8545 \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}'
```

## Variantes

- `eth_sendTransaction` desde una cuenta desbloqueada.
- `hardhat_setBalance` para modificar saldos.
- `hardhat_impersonateAccount` para suplantar una cuenta.
- Contratos con funciones sin control de acceso.
- Claves privadas en el código o en variables de entorno.

## Limitaciones

- El nodo debe ser accesible desde la red.
- Las cuentas deben estar desbloqueadas.
- El saldo puede ser de prueba sin valor real.
- La red puede requerir un fork o una configuración concreta.

## Mitigación y detección

- No exponer el nodo fuera de localhost.
- Usar redes de prueba sin fondos reales.
- Autenticar el RPC con un proxy y limitar métodos.
- Alertar de `eth_accounts`, `eth_sendTransaction` y cambios de saldo inesperados.

## Referencias

- <https://hardhat.org/hardhat-network/docs/overview>
- <https://ethereum.org/en/developers/docs/apis/json-rpc/>
- <https://attack.mitre.org/techniques/T1078/>
- <https://cwe.mitre.org/data/definitions/306.html>
