---
challenge: Wrong Spooky Season
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, reverse-shell, tshark]
---

# Wrong Spooky Season — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un PCAP contiene una reverse shell. Al seguir el stream TCP se ve el comando de conexión, la shell interactiva y la lectura de la flag. No hay cifrado.

## Enunciado y superficie

- Forensics, Easy, retirado.
- Se entrega un `.pcap`.
- El enunciado describe actividad sospechosa en Halloween.

```bash
capinfos capture.pcap
tshark -r capture.pcap -q -z conv,tcp
```

## Reconocimiento

- Tráfico TCP con un puerto alto.
- Un host interno conecta con un host externo.
- Hay payloads ASCII legibles.

## Análisis del código

No hay código que analizar. Se identifican los streams y se busca el que contiene una shell. El comando suele incluir `bash -i`, `nc` o `mkfifo`.

```bash
tshark -r capture.pcap -Y 'tcp contains "bash"' -T fields -e tcp.stream
```

## Explicación del fallo

La reverse shell viaja sin cifrar. Cualquiera con acceso al PCAP puede reconstruir la sesión, los comandos y la salida, incluida la flag.

## Reproducción local

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,<STREAM>
```

- Seguir el stream.
- Anotar el comando de conexión y el usuario.
- Extraer la salida de `cat`/`type`.

## Explotación

```bash
tshark -r capture.pcap -q -z follow,tcp,raw,<STREAM> | xxd -r -p
```

La flag aparece en la salida; se redacta.

## Evidencia

- Conversaciones TCP.
- Stream con la shell.
- Comando de conexión y salida redactada.

## Lecciones aprendidas

- Las shells sin TLS son triviales de reconstruir.
- Los puertos altos no implican cifrado.
- La correlación temporal ayuda a separar sesiones.

## Mitigaciones y detección

- Cifrar todo el tráfico y segmentar la red.
- Detectar conexiones salientes a puertos altos y procesos `nc`/`bash -i`.
- Retener PCAP solo el tiempo necesario.

## Referencias

- <https://www.hackthebox.com/challenges/Wrong%20Spooky%20Season>
- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/wrong-spooky-season/>
