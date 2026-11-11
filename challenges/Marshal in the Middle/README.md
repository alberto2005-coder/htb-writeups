---
challenge: Marshal in the Middle
category: Challenge
type: Forensics
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, pcap, tls, zeek, exfiltracion, wireshark]
---

# Marshal in the Middle — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según el índice histórico de retos y writeups públicos; no comprobado con sesión en HTB.
> Sin flags ni datos personales reales.

## TL;DR

Un ZIP entrega ocho logs de **Zeek**, un `bundle.pem`, un `secrets.log` y un PCAP de un servidor web comprometido. En `dns.log` se identifica al host atacante; el tráfico HTTPS se descifra en Wireshark con la clave de sesión y el certificado. Dentro hay exfiltración por `POST /api/api_post.php`: primero `/etc/passwd`, luego `/etc/shadow` y finalmente un volcado con datos de tarjetas y la marca del reto.

## Enunciado y superficie

- Categoría **Forensics**, dificultad **Medium**.
- Entrega: `Marshal in the Middle.zip` (contraseña habitual `hackthebox`).
- Contenido: logs de Zeek (`conn.log`, `dns.log`, `http.log`, `ssl.log`, etc.), `bundle.pem`, `secrets.log` y `chalcap.pcapng`.
- La pregunta es si se robaron datos y cuáles; no hay que explotar un servicio.

## Reconocimiento

```bash
sha256sum 'Marshal in the Middle.zip'
unzip -P hackthebox 'Marshal in the Middle.zip' -d marshal/
ls -la marshal/
capinfos marshal/chalcap.pcapng
```

Los logs de Zeek permiten ver la conversación sin abrir el PCAP:

```bash
cat marshal/dns.log | zeek-cut id.orig_h id.resp_h query | sort -u | head -40
cat marshal/conn.log | zeek-cut id.orig_h id.resp_h id.resp_p proto | sort | uniq -c | sort -nr | head
```

La actividad sospechosa sale de un host interno hacia un servidor web y hacia un servicio tipo Pastebin. La IP del atacante y la del servidor comprometido se confirman cruzando `dns.log`, `conn.log` y `http.log`.

## Explicación del fallo

El servidor web acepta y ejecuta un `POST` a `/api/api_post.php` sin autenticación ni controles de salida. El atacante usa esa función como canal de exfiltración: envía el contenido de ficheros del sistema y un volcado de base de datos a un servicio externo. El tráfico va por **HTTPS**, pero el reto entrega la clave de sesión (`secrets.log`) y la cadena de certificados (`bundle.pem`), así que el cifrado no protege la evidencia.

## Explotación

### Descifrar TLS

En Wireshark:

1. `Edit → Preferences → Protocols → TLS`.
2. En **(Pre)-Master-Secret log filename**, seleccionar `secrets.log`.
3. En **RSA keys list**, añadir `bundle.pem`.
4. Aplicar y abrir `chalcap.pcapng`.

El stream se descifra a partir del `Server Hello`. Los frames que documentan los writeups son:

| Frame | Contenido |
|---:|---|
| 5666 | inicio del stream descifrado |
| 5725 | `POST` con `/etc/passwd` |
| 7039 | `POST` con `/etc/shadow` |
| 9887 | volcado final con datos de tarjetas y la marca del reto |

```bash
tshark -r marshal/chalcap.pcapng -Y 'http.request.method == "POST"' \
  -T fields -e frame.number -e ip.src -e http.request.uri
```

No hace falta fuerza bruta: la clave está en el material entregado. Si el `secrets.log` no cubre una sesión, el `bundle.pem` solo sirve para validar la cadena, no para descifrar sin la clave privada.

### Exportar los objetos HTTP

La vía más rápida es `File → Export Objects → HTTP → Save All`, y buscar la marca del reto en los objetos:

```bash
mkdir -p http_objects
# guardar los objetos desde Wireshark en http_objects/
grep -RIn 'HTB{' http_objects/ | head
```

En Wireshark también se puede filtrar `http.file_data contains "HTB"`; el objeto que aparece es `api_post(4).php` en la mayoría de writeups. El contenido es el volcado exfiltrado, no un fichero del servidor.

## Evidencia

- `dns.log`/`conn.log` con el host interno y el destino externo.
- `secrets.log` y `bundle.pem` cargados en Wireshark.
- Frames 5725, 7039 y 9887 con los `POST`.
- Objetos HTTP exportados, con la marca del reto redactada.
- Sin flags ni datos de tarjetas reales.

## Lecciones aprendidas

- **HTTPS no es confidencialidad si la clave de sesión está en el mismo ZIP**: la evidencia y la clave viajan juntas.
- Los logs de Zeek permiten llegar al flujo relevante sin abrir el PCAP; el PCAP se usa después para descifrar y leer.
- `Export Objects → HTTP` reconstruye el cuerpo de los `POST` sin seguir el stream a mano.
- El frame 9887 es el objetivo: los anteriores son pasos intermedios (`passwd`, `shadow`).
- Un canal de exfiltración puede ser una API legítima del servidor comprometido.

## Mitigaciones y detección

- No registrar claves TLS de sesión junto a capturas de producción; separar evidencia y secretos.
- Autenticar `/api/api_post.php`, validar el tamaño y el tipo de los cuerpos y limitar la salida a dominios permitidos.
- Detección: `POST` anómalos a APIs internas, transferencias grandes desde servidores web, conexiones a Pastebin/servicios de pegado y lecturas de `/etc/passwd` o `/etc/shadow`.
- MITRE: T1041 (exfiltración por canal C2), T1048 (exfiltración por protocolo alternativo), T1071.001 (HTTP).
- Referencias: writeups de Justus Perlwitz y Phoenix Computing Solutions; documentación de Zeek y Wireshark TLS.

## Referencias

- <https://www.justus.pw/writeups/hack-the-box-challenges/marshal_in_the_middle.html>
- <https://www.phoenix-comp.com/HTB/Easy/Marshal-in-the-Middle>
- <https://jebidiah-anthony.github.io/chals/htb/challenges.html>
