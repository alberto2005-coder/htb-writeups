---
sherlock: APTNightmare
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, memory, cobalt-strike, linux, windows]
---

# APTNightmare — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales.

## Escenario

Una campaña APT compromete un servidor web Linux y utiliza el CEO como siguiente objetivo. Se entrega una captura de red, un volcado de memoria del servidor, un perfil de Ubuntu y una copia parcial del disco del CEO. Hay que reconstruir el acceso, el reverse shell, la persistencia y la entrega del segundo stage.

## Evidencias

- `traffic.pcapng`: captura de ~52 minutos.
- `Memory_WebServer.mem`: memoria del servidor web.
- `Ubuntu_5.3.0-70-generic_profile.zip`: `/boot` y `/tools`.
- `DiskImage_CEO-US.zip`: copia parcial de `C:` del CEO.

```bash
sha256sum traffic.pcapng Memory_WebServer.mem DiskImage_CEO-US.zip
capinfos traffic.pcapng
```

## Investigación

### 1. Inventario y triaje

Se empieza por la captura, porque da la línea temporal y los flujos:

```bash
tshark -r traffic.pcapng -q -z conv,tcp
tshark -r traffic.pcapng -Y 'http.request' -T fields -e frame.time -e ip.src -e http.host -e http.request.uri
```

Se identifican el host comprometido, el atacante y los puertos del reverse shell.

### 2. Línea temporal

- Primer contacto HTTP y explotación del servidor web.
- Conexión reversa y comandos interactivos.
- Modificación de `crontab` para persistencia.
- Descarga de un binario desde el servidor comprometido.
- Entrega del adjunto al CEO y ejecución en Windows.

La captura cubre 2024-02-05 de 02:30:40 a 03:23:02; se normaliza a UTC.

### 3. Artefacto clave

El PCAP contiene el canal del reverse shell. Al seguirlo se ven los comandos de persistencia y la descarga del segundo stage. En memoria, `strings` y `grep` permiten localizar el binario y la configuración del C2 cuando Volatility no reconoce el perfil.

```bash
strings Memory_WebServer.mem > mem.strings
grep -iE 'cron|wget|curl|powershell|\.exe' mem.strings | head
python3 1768.py -r download.exe
```

`1768.py` identifica el beacon de Cobalt Strike. En el disco del CEO, los LNK y el MFT revelan la ruta del adjunto y la tarea programada.

## Conclusiones

- El servidor Linux fue el punto de entrada y el C2 inicial.
- El atacante usó cron para persistir y distribuyó un binario a través del servidor comprometido.
- El CEO ejecutó un adjunto que instaló un beacon y una tarea programada.
- Los IOCs son la IP/puerto del C2, el hash del binario y el nombre del adjunto.

## Lecciones

- El PCAP puede reconstruir un reverse shell completo aunque no haya logs.
- `strings` sigue siendo útil cuando el perfil de memoria no carga.
- Un servidor web comprometido puede servir el segundo stage.
- La cadena completa cruza Linux y Windows; hay que mantener ambos timelines.

## Referencias

- <https://mwalkowski.com/post/sherlock-aptnightmare>
- <https://github.com/DidierStevens/DidierStevensSuite/blob/master/1768.py>
- <https://attack.mitre.org/techniques/T1059/004/>
