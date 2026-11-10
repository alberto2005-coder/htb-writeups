---
challenge: Obscure
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, webshell, keepass, john, ofuscacion]
type: Forensics
---

# Obscure — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; el flag no se publica.

## Enunciado

Se entrega la captura de tráfico de un servidor web comprometido y hay que reconstruir qué hizo el atacante y qué se llevó.

## Evidencias

```text
19-05-21_22532255.pcap    captura del incidente
```

## Método

### 1. Ver qué se habló

```bash
tshark -r 19-05-21_22532255.pcap -q -z conv,tcp
tshark -r 19-05-21_22532255.pcap -Y "http.request" -T fields -e http.request.method -e http.request.uri | sort | uniq -c
```

El interés está en las peticiones `POST` a un único script, siempre con el mismo nombre: ahí viaja el payload.

### 2. Seguir el flujo completo

```bash
tshark -r 19-05-21_22532255.pcap -q -z follow,tcp,ascii,0
```

En el cuerpo del `POST` aparece un parámetro con un blob **base64**; al decodificarlo no sale PHP legible, sino datos binarios: hay otra capa.

### 3. Deshacer la ofuscación

El patrón habitual es base64 → **zlib** → **XOR** con una clave de un byte o derivada de una cadena del propio blob:

```python
import base64, zlib
raw = base64.b64decode(blob)
data = zlib.decompress(raw)
print(bytes(b ^ 0x5a for b in data).decode("latin-1"))
```

El resultado es el **webshell** que el atacante subió: un script PHP con el ejecutor de comandos (`support.php` en la raíz del sitio). Esa es la prueba del acceso inicial, y también la respuesta a «¿qué dejó instalado?».

### 4. Qué más se descargó

Repitiendo el seguimiento de cada flujo aparecen dos ficheros más: un `to-do.txt` de la víctima y una base de datos de **KeePass** (`pwdb.kdbx`). La extracción se hace desde el propio `tshark`:

```bash
tshark -r 19-05-21_22532255.pcap --export-objects http,exported/
ls -l exported/
```

### 5. Abrir el gestor

```bash
keepass2john pwdb.kdbx > kdbx.hash
john --wordlist=/usr/share/wordlists/rockyou.txt kdbx.hash
keepassxc-cli show -s pwdb.kdbx <entrada>
```

Con la contraseña crackeada se abre la base y el flag está en una de las entradas.

## Conclusiones

- El compromiso fue una **subida de webshell** vía HTTP `POST`, no una explotación de servicio.
- La ofuscación del payload es base64 + compresión + XOR: tres capas, todas reversibles sin la clave del atacante.
- El robo real es el gestor de contraseñas: la captura contiene la base y su contraseña cae por diccionario.

## Lecciones

- En un PCAP, `follow,tcp` + `--export-objects` resuelve el 90 % del trabajo antes de abrir Wireshark.
- Un blob base64 que no decodifica a texto es señal de compresión, no de cifrado.
- Un `.kdbx` en el tráfico es un compromiso de todas las credenciales que contenga.
- Mitigación: validación de subidas, permisos de escritura fuera del docroot y gestor de contraseñas con contraseña maestra fuerte.
