---
topic: Multisig thresholds
tags: [blockchain, solidity, multisig, access-control, signatures]
---

# Multisig thresholds

[🌐 English](multisig-thresholds.en.md) | **Español**

## Concepto

Una wallet multifirma exige que un número mínimo de firmantes autorice una acción. El umbral debe comprobarse explícitamente y las firmas deben estar ligadas a la operación, la cadena y el contrato. Un bucle que recorre firmas no implementa por sí mismo un umbral.

## Cuándo aplica

- Tesorerías y contratos de crowdfunding.
- Gobernanza de protocolos y upgrades.
- Retiros o cierres controlados por un consejo.
- Cualquier función que reciba un array de firmas.

## Requisitos y condiciones

- Lista de firmantes autorizados.
- Mensaje canónico que incluya operación, destinatario, cadena y nonce.
- Verificación ECDSA o equivalente.
- Comprobación de firmas duplicadas y del número mínimo.

## Procedimiento

1. Definir el umbral `M` de `N` firmantes.
2. Construir el hash de la operación completa.
3. Verificar cada firma y recuperar el firmante.
4. Rechazar firmantes desconocidos y repetidos.
5. Exigir `signatures.length >= M` antes de ejecutar.
6. Ejecutar la acción solo si se alcanzó el umbral.

```solidity
require(signatures.length >= threshold, "Not enough signatures");
require(uniqueSigners == threshold, "Invalid signers");
```

## Variantes

- Multifirma on-chain con lista de owners.
- Firmas off-chain verificadas en el contrato.
- Threshold signatures (por ejemplo, Schnorr o MPC).
- Timelock más multisig para operaciones críticas.

## Limitaciones

- Un array vacío puede saltar el bucle si no se valida la longitud.
- Las firmas pueden reutilizarse si no hay nonce.
- El destinatario y el contrato deben formar parte del mensaje firmado.
- Los cambios de owners requieren su propio control de acceso.

## Mitigación

- Validar el umbral de forma explícita y separada del bucle.
- Incluir `address(this)`, `chainId` y un nonce en el hash.
- Normalizar firmas ECDSA y rechazar valores no canónicos.
- Evitar `selfdestruct` en lógica de negocio.
- Añadir timelock y pruebas de invariantes.

## Detección

- Alertar de llamadas con arrays vacíos o menores que el umbral.
- Monitorizar cambios de owners y de umbral.
- Revisar operaciones con destinatarios inesperados.
- Comparar el número de firmas con el número de firmantes únicos.

## Referencias

- <https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#ECDSA>
- <https://swcregistry.io/docs/SWC-105>
- <https://attack.mitre.org/techniques/T1548/>
