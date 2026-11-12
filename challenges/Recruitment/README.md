---
challenge: Recruitment
type: Blockchain
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [blockchain, ethereum, smart-contract, rpc, foundry, business-ctf]
---

# Recruitment — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Reto introductorio de blockchain: se conecta al RPC, se inspecciona el contrato y se envía una transacción que cumple las restricciones del `require`. Al superar la comprobación, el servicio entrega la flag.

## Enunciado y superficie

- Blockchain, Very Easy, retirado (Business CTF 2024).
- Se entregan RPC, dirección del contrato y una interfaz de gestión.
- El objetivo es cumplir las condiciones del contrato.

## Reconocimiento

```bash
nc <IP> <PORT>
cast block-number --rpc-url <RPC>
cast code <CONTRACT> --rpc-url <RPC>
```

Se revisan las funciones públicas y los eventos. Si hay código fuente, se lee el `require` y el estado inicial.

## Análisis

1. Se identifica la función que valida la condición.
2. Se revisan los tipos (`uint`, `address`, `string`) y los límites.
3. Se calcula el valor/argumento necesario.
4. Se simula con `cast call` antes de enviar.
5. Se envía la transacción y se consulta el estado.

```bash
cast call <CONTRACT> "<function>(<args>)" <args> --rpc-url <RPC>
cast send <CONTRACT> "<function>(<args>)" <args> --private-key <KEY> --rpc-url <RPC>
```

## Explicación del fallo

El contrato confía en una condición simple que el atacante puede satisfacer. No hay control de acceso ni aleatoriedad segura; el estado es público y manipulable.

## Reproducción local

1. Levantar Anvil.
2. Desplegar el contrato con Foundry.
3. Repetir la llamada.
4. Verificar el cambio de estado.
5. Solicitar la flag al servicio.

## Evidencia

- Salida de `cast code`/`cast call`.
- Transacción y recibo.
- Estado final.
- Flag redactada.

## Lecciones aprendidas

- Los contratos son state machines públicas.
- `require` es la puerta lógica a superar.
- Simular antes de enviar evita perder gas.
- Foundry/`cast` agiliza la interacción.

## Mitigación y detección

- No usar condiciones triviales como autorización.
- Aplicar control de acceso y firmas.
- Revisar la lógica con tests y fuzzing.
- Monitorizar transacciones anómalas.

## Referencias

- <https://book.getfoundry.sh/>
- <https://www.hackthebox.com/>
- <https://ethereum.org/en/developers/docs/smart-contracts/security/>
