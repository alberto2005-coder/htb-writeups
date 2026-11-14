---
challenge: POOF
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, memory, pyinstaller, ransomware, aes-cfb]
---

# POOF — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un PCAP, un volcado de memoria y un PDF cifrado reconstruyen un ransomware. El tráfico revela la descarga de un tar.gz con un binario `configure` compilado con PyInstaller. Al extraerlo y decompilarlo aparecen la clave y el IV de AES-CFB; con ellos se descifra el PDF y se obtiene la flag.

## Enunciado y superficie

- Forensics, Easy, retirado.
- Se entregan `poof_capture.pcap`, `mem.dmp`, `candy_dungeon.pdf.boo` y un perfil de Ubuntu.
- El escenario pide identificar la URL maliciosa, el proceso y el algoritmo de cifrado.

```bash
unzip -l POOF.zip
```

## Reconocimiento

- El PCAP contiene tráfico HTTP y una descarga de `pygaming-dev-13.37.tar.gz`.
- El archivo `.boo` es el PDF cifrado.
- El volcado de memoria y el perfil permiten validar el proceso, pero el PCAP ya da la pista principal.

```bash
tshark -r poof_capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

## Análisis del código

El tar.gz contiene un binario `configure`. `file` y `strings` muestran referencias a Python 3.6 y a PyInstaller; no es un binario nativo al uso.

```bash
tar -xzf pygaming-dev-13.37.tar.gz
file pygaming-dev-13.37/configure
strings -n 8 pygaming-dev-13.37/configure | grep -i pyinstaller
```

Se extrae el archivo con `pyinstxtractor` y se decompila `configure.pyc` con `uncompyle6`. El código contiene una función de cifrado AES-CFB con clave e IV embebidos y una función que renombra cada archivo a `.boo`.

## Explicación del fallo

El ransomware usa una clave simétrica incluida en el propio binario. No hay intercambio de claves ni cifrado asimétrico: cualquiera que analice el ejecutable puede descifrar los archivos. La función de cifrado y la nota de rescate están en el bytecode.

```python
cipher = AES.new(key, AES.MODE_CFB, iv)
open(filename, "wb").write(cipher.encrypt(data))
```

## Reproducción local

```bash
python3 -m venv venv
. venv/bin/activate
pip install pycryptodome
python3 - <<'PY'
from Crypto.Cipher import AES
key = b"<KEY>"
iv = b"<IV>"
data = open("candy_dungeon.pdf.boo", "rb").read()
open("candy_dungeon.pdf", "wb").write(AES.new(key, AES.MODE_CFB, iv).decrypt(data))
PY
```

## Explotación

1. Extraer el tar.gz del PCAP.
2. Identificar el binario y el proceso `configure`.
3. Extraer el bytecode con `pyinstxtractor`.
4. Decompilar con `uncompyle6`.
5. Leer la clave y el IV.
6. Descifrar el PDF y calcular su MD5.

```bash
md5sum candy_dungeon.pdf
```

El MD5 y la flag se redactan.

## Evidencia

- URL de descarga y nombre del proceso.
- `file` y `strings` del binario.
- Función de cifrado decompilada, con clave redactada.
- PDF descifrado y MD5 redactado.

## Lecciones aprendidas

- Los binarios de PyInstaller se pueden extraer y decompilar.
- Una clave embebida no protege un ransomware.
- El PCAP permite reconstruir la cadena aunque la memoria sea grande.

## Mitigaciones y detección

- Bloquear descargas de binarios desde hosts no confiables.
- Analizar ejecutables con PyInstaller antes de ejecutarlos.
- Monitorizar la creación masiva de archivos con extensiones anómalas.
- Alertar de procesos que cifran directorios de usuario y de conexiones HTTP a archivos comprimidos.

## Referencias

- <https://www.hackthebox.com/challenges/POOF>
- <https://github.com/extremecoders-re/pyinstxtractor>
- <https://attack.mitre.org/techniques/T1486/>
- <https://attack.mitre.org/techniques/T1059/006/>
