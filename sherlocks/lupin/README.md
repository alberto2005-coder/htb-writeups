---
sherlock: Lupin
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, pe, clipboard-hijacking, cryptocurrency, ssdp, static-analysis]
---

# Lupin — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una muestra `optimize.exe` se comparte como herramienta de optimización. La usuaria Samira nota que la dirección de wallet que copia cambia antes de pegarla. Se pide analizar el binario, identificar persistencia, C2 y el mecanismo de robo.

## Evidencias

- `optimize.exe`, PE de 32 bits, 81.920 bytes.
- No se ejecuta la muestra; el análisis es estático.
- Herramientas: `pefile`, Capstone, `strings`.

```bash
sha256sum optimize.exe
file optimize.exe
python3 -c "import pefile; pe=pefile.PE('optimize.exe'); print(hex(pe.OPTIONAL_HEADER.ImageBase))"
```

## Investigación

### 1. Inventario y triaje

La entropía del archivo es media (≈6,4), no está empaquetado y las cadenas se leen. El binario importa funciones de portapapeles, WinINet y red.

```bash
python3 - <<'PY'
import math, collections
d = open("optimize.exe", "rb").read()
c = collections.Counter(d)
print(-sum(v/len(d)*math.log2(v/len(d)) for v in c.values()))
PY
```

### 2. Persistencia y evasión

El malware se copia a ubicaciones del sistema con un nombre que parece un servicio, `syscrondvr.exe`. Antes de actuar comprueba su propio nombre y consulta la configuración regional; si el locale no coincide, se detiene.

- Copia con nombre fijo para mezclarse con servicios.
- `GetLocaleInfoA` como puerta geográfica.
- `DeleteUrlCacheEntry` antes de cada petición para forzar datos frescos del C2.

### 3. Robo del portapapeles

El binario se registra en la cadena de visores con `SetClipboardViewer` y reacciona a `WM_DRAWCLIPBOARD`. Cuando detecta una dirección de wallet, abre el portapapeles, lo vacía y escribe la dirección del atacante con `SetClipboardData`.

```text
SetClipboardViewer → WM_DRAWCLIPBOARD → OpenClipboard → EmptyClipboard → SetClipboardData
```

También envía `M-SEARCH` SSDP a `239.255.255.250:1900`, comportamiento de descubrimiento de red.

### 4. Atribución y blockchain

La dirección del atacante está hardcodeada. Se resuelve un nombre ENS de la víctima y se sigue la transacción en un explorador de bloques; el movimiento coincide con la fecha del incidente. El conjunto de comportamientos (clipper, copia con nombre de servicio, propagación por USB) encaja con la familia Phorpiex.

## Conclusiones

- El malware sustituye direcciones de wallet en el portapapeles.
- La persistencia usa un nombre de servicio y una comprobación de locale.
- El C2 se consulta con la caché invalidada.
- La trazabilidad on-chain permite confirmar el impacto.

## Lecciones

- Un binario sin UI que registra un visor de portapapeles es sospechoso.
- Verificar la wallet después de pegar es una defensa simple y eficaz.
- La atribución por comportamiento debe confirmarse con hashes e inteligencia.

## Referencias

- <https://www.hackthebox.com/sherlocks/Lupin>
- <https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard>
- <https://attack.mitre.org/techniques/T1115/>
- <https://attack.mitre.org/techniques/T1091/>
