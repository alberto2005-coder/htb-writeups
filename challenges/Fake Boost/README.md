---
challenge: Fake Boost
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, powershell, base64, aes, c2, phishing]
---

# Fake Boost — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (Cyber Apocalypse 2024). Reto resuelto; sin flags reales.

## TL;DR

Una captura de red contiene una campaña de phishing que regala "Discord Nitro". El señuelo descarga un PowerShell ofuscado que **invierte y decodifica en base64** una cadena antes de ejecutarla. Desofuscado, el script recoge datos del usuario (incluido el token de Discord), los cifra con **AES-CBC** y los envía por HTTP a `192.168.116.135:8080/rj1893rj1joijdkajwda`. Todo el caso se resuelve exportando objetos HTTP y desofuscando sin ejecutar nada.

## Enunciado y superficie

- Forensics, dificultad 2/5 en el índice oficial del evento.
- Se entrega `forensics_fake_boost.zip`, que contiene una única captura: `capture.pcapng`.
- No hay binario del señuelo: el artefacto es el tráfico.

## Reconocimiento

```bash
capinfos capture.pcapng
tshark -r capture.pcapng -q -z io,phs
tshark -r capture.pcapng -q -z conv,tcp
```

```bash
mkdir -p out
tshark -r capture.pcapng --export-objects http,out
ls -l out
```

Los objetos HTTP incluyen el HTML del señuelo, el ZIP/EXE descargado y las peticiones `POST` de exfiltración.

## Análisis del código

El script de PowerShell aparece en el cuerpo de una respuesta. Ofuscado se ve así:

```powershell
$b64 = '...'
$rev = -join ($b64[-1..-($b64.Length)])
$dec = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($rev))
Invoke-Expression $dec
```

Es decir: la cadena está invertida **y** en base64. Cualquier orden distinto (decodificar sin invertir) devuelve basura, que es el error habitual al copiar el bloque a mano.

Desofuscado, el script:

1. Lee el token de Discord de `%APPDATA%\discord\Local Storage\leveldb`.
2. Recoge información del sistema.
3. Cifra el conjunto con **AES-CBC** (clave y IV embebidos en el propio script).
4. Envía el resultado por `POST` a una URL del atacante.

## Explicación del fallo

No es una vulnerabilidad: es una cadena de ingeniería social con ofuscación trivial. El valor forense está en reconstruir el orden de las transformaciones y en identificar el canal de salida, no en "romper" nada.

El cifrado AES no protege nada: la clave viaja en el mismo script que el atacante dejó en el equipo, así que el analista descifra con ella.

## Reproducción local

```bash
tshark -r capture.pcapng -Y 'http.response' -T fields -e http.file_data > respuestas.txt
```

Desofuscar sin ejecutar (Ruby/Python, `-join` y `reverse`):

```python
import base64, re
s = open('respuestas.txt', encoding='utf-8', errors='replace').read()
b64 = re.search(r"\$b64\s*=\s*'([^']+)'", s).group(1)
print(base64.b64decode(b64[::-1]).decode('utf-8', 'replace')[:800])
```

## Explotación

1. Exportar objetos y localizar el script y el `POST` de exfiltración:

```bash
tshark -r capture.pcapng -Y 'http.request.method == "POST"' \
  -T fields -e ip.dst -e tcp.dstport -e http.request.uri
```

```text
192.168.116.135   8080   /rj1893rj1joijdkajwda
```

2. Extraer el cuerpo cifrado del `POST` (el `http.file_data` del flujo) y el par clave/IV del script desofuscado.

3. Descifrar con AES-CBC:

```python
from Crypto.Cipher import AES
pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
print(pt.rstrip(b'\x00'))
```

4. Del JSON descifrado se leen el usuario, el host y el token, y el flag que el reto coloca en el flujo.

Herramienta opcional: **PowerDecode 2.7** automatiza el desempaquetado del PowerShell ofuscado, pero el análisis a mano con `tshark` + CyberChef llega igual.

## Evidencia

- Listado de objetos HTTP, la URL de exfiltración y el JSON descifrado recortado.
- Sin flags reales: los valores viven en `private/`.

## Lecciones aprendidas

- `--export-objects http` convierte un PCAP en ficheros: es el primer comando, no el último.
- Invertir y luego decodificar es una ofuscación de una línea; el orden importa y hay que respetarlo.
- Que el malware cifre la exfiltración no es un obstáculo si la clave está en el propio script.
- El destino `192.168.116.135:8080` con URI aleatoria es el IOC que se lleva a un bloqueo de proxy.

## Mitigaciones y detección

- Bloquear adjuntos y descargas con doble extensión; el señuelo "Nitro gratis" es el gancho clásico.
- Proxy con inspección de `POST` a IPs sin dominio y de URIs aleatorias.
- Detección: PowerShell con `FromBase64String` + `Invoke-Expression` (4104 con ambos), procesos que leen el `leveldb` de Discord y conexiones salientes al puerto 8080 desde estaciones.
- Rotar el token de Discord y credenciales del navegador tras el incidente.

MITRE: T1566.002 (spearphishing link), T1059.001 (PowerShell), T1027 (obfuscated files or information), T1041 (exfiltration over C2), T1555.003 (credentials from web browsers).

## Referencias

- <https://github.com/hackthebox/cyber-apocalypse-2024>
- <https://ctftime.org/writeup/38843>
- <https://v0lk3n.github.io/writeup/HTB-CyberApocalypse2024/HTB-CyberApocalypse2024-WriteUp.html>
- <https://www.wireshark.org/docs/man-pages/tshark.html>
