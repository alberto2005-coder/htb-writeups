---
topic: Ethereum — JSON-RPC y datos en bloques
tags: [linux, ethereum, json-rpc, blockchain, osint]
---

# Ethereum — JSON-RPC y datos en bloques

[🌐 English](ethereum-jsonrpc-blockchain.en.md) | **Español**

## Concepto

Un nodo Ethereum expone JSON-RPC para consultar bloques y transacciones. Los datos de entrada de una transacción son hex y pueden contener mensajes, credenciales o rutas. Si el nodo es accesible, la blockchain se convierte en un canal de datos público y permanente que se puede enumerar sin autenticación.

## Cuándo aplica

- El puerto `8545` o un proxy JSON-RPC está accesible.
- La aplicación escribe mensajes o configuraciones en transacciones.
- Se busca un canal de datos que no dependa de la base de datos principal.

## Procedimiento

1. Confirmar el método JSON-RPC y la cadena.
2. Consultar el último bloque con transacciones completas.
3. Decodificar los campos `input` de hex a texto.
4. Reutilizar los datos encontrados en el siguiente servicio.

## Comandos

```bash
curl -s -X POST http://<HOST>:8545 -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",true],"id":1}'
# Decodificar un input hex
python3 -c "print(bytes.fromhex('<HEX>').decode(errors='ignore'))"
```

## Variantes

- Recorrer bloques históricos con `eth_getBlockByNumber`.
- Consultar transacciones por hash con `eth_getTransactionByHash`.
- Usar un explorador público si el nodo no está expuesto.

## Limitaciones

- El nodo puede limitar métodos o exigir autenticación.
- Los datos pueden estar comprimidos o cifrados.
- La sincronización puede no incluir bloques recientes.

## Mitigación

- No almacenar secretos en la blockchain.
- Restringir JSON-RPC a loopback y autenticar.
- Monitorizar consultas a bloques y transacciones.

## Detección

- Consultas masivas a `eth_getBlockByNumber`.
- Acceso a JSON-RPC desde hosts no habituales.
- Datos sensibles en el campo `input`.

## Referencias

- [0xdf — BlockBlock](https://0xdf.gitlab.io/2025/03/29/htb-blockblock.html)
- [Ethereum — JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- [CWE-200 — Exposure of Sensitive Information](https://cwe.mitre.org/data/definitions/200.html)
