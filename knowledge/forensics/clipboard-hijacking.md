---
topic: Secuestro del portapapeles
tags: [forensics, malware, clipboard, cryptocurrency, windows, phorpiex]
---

# Secuestro del portapapeles

[🌐 English](clipboard-hijacking.en.md) | **Español**

## Concept

Un clipper se registra como visor del portapapeles de Windows y reacciona a `WM_DRAWCLIPBOARD`. Cuando detecta una dirección de wallet, la sustituye por la del atacante. La víctima pega una dirección distinta de la que copió y la transacción se pierde.

## Cuándo aplica

- Binarios que importan `SetClipboardViewer`, `OpenClipboard` o `SetClipboardData`.
- Usuarios que reportan direcciones de criptomonedas alteradas.
- Malware con persistencia y comprobación de locale.
- Muestras que consultan un C2 antes de actuar.

## Procedimiento

1. Revisar imports y cadenas del binario.
2. Confirmar el registro en la cadena de visores.
3. Localizar el patrón de wallet y la dirección de reemplazo.
4. Revisar persistencia y C2.
5. Correlacionar con la transacción on-chain.

```text
SetClipboardViewer → WM_DRAWCLIPBOARD → OpenClipboard
→ GetClipboardData → EmptyClipboard → SetClipboardData
```

## Variantes

- Sustitución de direcciones BTC, ETH o USDT.
- Copia del binario con nombre de servicio.
- Comprobación de locale para evitar países concretos.
- Propagación por USB.
- Uso de ENS o dominios parecidos.

## Limitaciones

- El usuario debe copiar una dirección válida.
- El formato debe coincidir con el patrón buscado.
- Algunos EDR bloquean la manipulación del portapapeles.
- La dirección de reemplazo puede estar inactiva.

## Mitigación y detección

- Verificar la dirección después de pegar y antes de firmar.
- Usar hardware wallet con pantalla de confirmación.
- Bloquear binarios sin firma y monitorizar visores del portapapeles.
- Alertar de procesos que llaman a `SetClipboardData` y de cambios de wallet.

## Referencias

- <https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard>
- <https://attack.mitre.org/techniques/T1115/>
- <https://attack.mitre.org/techniques/T1091/>
- <https://www.cisa.gov/known-exploited-vulnerabilities-catalog>
