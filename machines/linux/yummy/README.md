---
machine: Yummy
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, rsa, sqli, mercurial, rsync]
---

# Yummy — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La exportación de calendarios concatena el nombre del archivo y permite un directory traversal para leer el código y los crons. La cookie JWT está firmada con RSA y la clave pública permite recuperar la privada; con el token de admin se accede al panel. Una SQLi escribe un script en el directorio de un cron, lo que da `www-data`; un repositorio Mercurial filtra credenciales y un hook permite pasar a `dev`, que ejecuta `rsync` como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 24.04 y `80/tcp` Caddy con `yummy.htb`.
- La web permite registrar usuarios, reservar mesas y exportar un `.ics`.
- El JWT de sesión usa RSA y el `kid` apunta a una clave pública.

## Enumeración

- `/export/../../../../etc/passwd` devuelve archivos; el traversal se repite para leer el código y `/etc/crontab`.
- El repositorio incluye la clave pública RSA del JWT y una contraseña de base.
- `RsaCtfTool` recupera la clave privada y permite firmar un token de admin.

## Foothold

Se firma un JWT con el rol de admin y se accede al panel. La SQLi del panel permite `INTO OUTFILE` en un directorio que un cron ejecuta; se escribe un script que lanza una reverse shell.

```bash
python3 jwt_tool.py -T <TOKEN> -S hs256 -p <KEY>
# o firmar con la clave RSA recuperada
# en el panel: SQLi -> SELECT ... INTO OUTFILE '/opt/.../script.sh'
```

## Movimiento lateral

La shell es `www-data`. En el sistema hay un repositorio Mercurial con credenciales de `qa` en commits antiguos; `qa` puede escribir un hook de Mercurial que se ejecuta al hacer `pull` o `commit`.

## Escalada de privilegios

El hook de Mercurial ejecuta código como `dev`. `dev` puede ejecutar `rsync` como root; se usa `-e` para lanzar una shell o se escribe en un destino privilegiado.

```bash
sudo -l
sudo rsync -e 'sh -c "sh 0<&2 1>&2"' <SRC> <DST>
```

## Evidencia

- Traversal en `/export` y código/crons leídos.
- JWT de admin firmado y SQLi con escritura.
- Credenciales de `qa`, hook de Mercurial y `rsync` como root.

## Lecciones aprendidas

- La concatenación de rutas en exportaciones permite traversal.
- Una clave RSA pública puede ser suficiente para recuperar la privada si es débil.
- Los hooks de Mercurial y `rsync` con `-e` son vectores de ejecución.

## Mitigación y detección

- Normalizar rutas y usar identificadores en lugar de nombres.
- Rotar claves JWT y usar algoritmos simétricos con secretos fuertes.
- Revisar hooks de Mercurial y limitar `rsync` privilegiado.

## Referencias

- [0xdf — Yummy](https://0xdf.gitlab.io/2025/02/22/htb-yummy.html)
- [IppSec — Yummy](https://www.youtube.com/watch?v=w6nYrsKsYBQ)
- [Hack The Box — Yummy](https://app.hackthebox.com/machines/yummy)
