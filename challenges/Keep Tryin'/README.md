---
challenge: Keep Tryin'
type: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, pcap, dns-exfil, base64url, rc4]
---

# Keep Tryin' — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Un PCAP de **26 paquetes** con dos `POST` y consultas **DNS TXT**. El primer subdominio decodifica a `secret.txt|1`: nombre de fichero y número de parte, es decir, exfiltración por DNS. Las partes se concatenan, se descifran con **RC4** usando la clave del `POST /flag` y sale un ZIP con `secret.txt`.

## Enunciado y superficie

`keeptrying.zip` (contraseña `hackthebox`) → `keeptryin.pcap`. Nada más: no hay servidor ni binario, la evidencia es el tráfico.

## Reconocimiento

```bash
tshark -r keeptryin.pcap | head -40
tshark -r keeptryin.pcap -Y 'http.request.method=="POST"' -T fields -e http.request.uri -e http.file_data
tshark -r keeptryin.pcap -Y 'dns.qry.type==16' -T fields -e dns.qry.name
```

## Explicación del fallo

Dos piezas sueltas que sólo cobran sentido juntas:

- `POST /flag` envía la cadena **`TryHarder`**: parece ruido, pero es la clave simétrica.
- `POST /lootz` envía `S2VlcCB0cnlpbmcsIGJ1ZmZ5Cg==`, que decodifica a *«Keep trying, buffy»*: una pista, no un dato.
- Las consultas TXT van a `<parte>.totallylegit[.]com`, con el trozo de fichero como subdominio.

```text
init.c2VjcmV0LnR4dHwx.totallylegit.com
```

`c2VjcmV0LnR4dHwx` no decodifica con base64 estándar porque usa el alfabeto **base64url** (`-` y `_`). Con el alfabeto correcto sale `secret.txt|1`.

## Explotación

1. **Recoger y ordenar**: se toman los subdominios, se separa `init` y el dominio, y se ordena por el índice tras el `|`.
2. **Concatenar** los trozos decodificados en orden.
3. **Descifrar**: el resultado no es texto (`file` dice `data`); con RC4 y la clave `TryHarder` aparecen los bytes mágicos `PK`.

```text
From Base64 (url safe) → RC4 (key: TryHarder) → Unzip
```

4. **Abrir** el ZIP: dentro está `secret.txt` con la flag.

## Evidencia

- Salidas recortadas de `tshark`; sin flags ni claves publicadas.
- Los valores reales viven en `private/`.

## Lecciones aprendidas

- **base64 vs base64url**: el alfabeto cambia y con el equivocado la decodificación falla.
- **Orden de las partes**: sin el índice del subdominio el ZIP sale corrupto.
- **`file` antes de adivinar**: `data` delata cifrado; `PK` confirma que el inverso es correcto.
- **Ruido aparente**: el `POST /flag` era la clave; descartar «lo que no se entiende» cuesta el reto.

- DNS es un canal de exfiltración habitual porque casi nunca se bloquea.
- Un prefijo con nombre de fichero y número de parte delata la reconstrucción.
- RC4 con clave débil no protege nada: es ofuscación.
- Mitigación: monitorizar consultas TXT largas y con alta entropía, y bloquear resolutores no autorizados.
