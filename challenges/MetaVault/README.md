---
challenge: MetaVault
type: Blockchain
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, metadata, bytecode, sourcify, business-ctf]
---

# MetaVault — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un contrato “MetaVault” esconde un secreto en su metadata. Se obtiene el bytecode, se verifica/descompila con Sourcify y se localiza la cadena embebida; con ella se ejecuta la función de emergencia y se vacía el vault.

## Enunciado y superficie

- Blockchain, Easy, retirado (Business CTF 2024).
- Se entregan RPC, dirección y una interfaz de gestión.
- El objetivo es vaciar los fondos del contrato.

## Reconocimiento

```bash
cast code <CONTRACT> --rpc-url <RPC>
cast call <CONTRACT> "owner()(address)" --rpc-url <RPC>
```

El bytecode incluye la metadata de Solidity (`a264...`). Se extrae y se envía a un verificador/descompilador:

```text
https://playground.sourcify.dev/
```

## Análisis

1. Se identifica la metadata y la versión del compilador.
2. Se reconstruye la interfaz y las funciones públicas.
3. Se busca una cadena/constante en la metadata o en el bytecode.
4. Se localiza la función `emergency` o similar que transfiere el balance.
5. Se llama con el secreto y se confirma el cambio de balance.

```bash
cast send <CONTRACT> "emergency(string)" "<secret>" --rpc-url <RPC> --private-key <KEY>
cast balance <CONTRACT> --rpc-url <RPC>
```

## Explicación del fallo

La metadata del contrato filtra información y la función privilegiada se protege con un secreto estático. Cualquiera que lea el bytecode puede invocarla.

## Reproducción local

1. Desplegar el contrato en Anvil.
2. Extraer la metadata.
3. Verificar el código.
4. Llamar a la función.
5. Comprobar que el balance queda a cero.

## Evidencia

- Bytecode y metadata.
- Código verificado/descompilado.
- Transacción y balance final.
- Flag redactada.

## Lecciones aprendidas

- La metadata de Solidity es pública.
- Un secreto en bytecode no es un secreto.
- La verificación de contratos acelera el análisis.
- Las funciones de emergencia son objetivos críticos.

## Mitigación y detección

- No incluir secretos en el contrato.
- Usar control de acceso robusto y multisig.
- Auditar funciones privilegiadas.
- Monitorizar retiradas inesperadas.

## Referencias

- <https://wepfen.github.io/writeups/metavault>
- <https://docs.sourcify.dev/>
- <https://book.getfoundry.sh/>
