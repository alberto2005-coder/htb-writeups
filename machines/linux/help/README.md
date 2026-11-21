---
machine: Help
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, graphql, helpdeskz, sqli, upload-bypass, kernel, cve-2017-16995, privesc]
---

# Help — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Hay dos caminos. El primero enumera una API GraphQL, obtiene credenciales de HelpDeskZ y explota una SQLi autenticada para volcar la base, de donde salen credenciales SSH. El alternativo, que 0xdf considera el que usó la mayoría, es un bypass de subida no autenticado en HelpDeskZ: se sube una webshell PHP y se fuerza la ruta del archivo. Para root se prueban exploits de kernel: CVE-2017-16995 con `44298.c` y `45010.c`, y CVE-2017-5899 con el script de `s-nail-privsep`; cualquiera de los tres da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22`: OpenSSH 7.2p2 Ubuntu.
- `80`: Apache httpd 2.4.18 con HelpDeskZ.
- `3000`: Node.js Express, API GraphQL.

```bash
echo '<IP> help.htb' | sudo tee -a /etc/hosts
gobuster dir -u http://help.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El puerto `3000` expone GraphQL. La introspección muestra consultas de usuarios y credenciales; con una consulta adecuada se obtienen usuarios y contraseñas de HelpDeskZ.

```graphql
{ User { username password } }
```

Con esas credenciales se entra en HelpDeskZ, una aplicación de tickets. La búsqueda de tickets concatena el parámetro en SQL, lo que permite una inyección autenticada. `sqlmap` con la cookie de sesión vuelca la base y aparecen credenciales del sistema.

## Foothold

La ruta alternativa no necesita credenciales: HelpDeskZ 1.0.2 valida mal la extensión en la subida de adjuntos. Se sube una webshell PHP y se busca la ruta generada dentro de `uploads/tickets/`; el script de Exploit-DB `40300.py` automatiza el proceso.

```bash
searchsploit helpdeskz
python3 40300.py http://help.htb/support/uploads/tickets/ cmd.php
```

Con la webshell o con las credenciales de la base se obtiene una shell como `help`.

## Movimiento lateral

No hay otro host. La enumeración del sistema muestra la versión del kernel y los permisos del usuario. `help` no tiene `sudo`, así que la escalada depende del kernel.

## Escalada de privilegios

El kernel es Ubuntu 4.4.0-116. Se prueban tres exploits:

- **CVE-2017-16995:** corrupción de memoria en el verificador BPF; `44298.c` y `45010.c` compilan y dan root.
- **CVE-2017-5899:** directory traversal en el helper setuid de S-nail; el script `s-nail-privsep` compite con el helper y deja una shell setuid.

```bash
gcc -o a 44298.c && ./a
gcc -o a 45010.c && ./a
./a.sh
id
```

Cualquiera de las tres rutas termina en UID 0.

## Evidencia

- Introspección GraphQL y credenciales de HelpDeskZ.
- SQLi autenticada y volcado de la base.
- Subida de webshell con extensión PHP y ejecución.
- `uname -a` con el kernel 4.4.0-116.
- Ejecución de los exploits y `id` con UID 0.

## Lecciones aprendidas

- GraphQL mal protegido puede exponer credenciales completas.
- Una SQLi autenticada sigue siendo crítica si el usuario tiene acceso a datos sensibles.
- La validación de subidas por extensión o lista negra se evade con facilidad.
- Un kernel antiguo convierte una shell de usuario en root con exploits públicos.
- CVE-2017-5899 es de S-nail, no del kernel, aunque se agrupe con los exploits de elevación.

## Mitigaciones y detección

- Deshabilitar la introspección y limitar los campos de GraphQL en producción.
- Parametrizar las consultas SQL y revisar el acceso a tickets.
- Validar subidas por contenido, extensión permitida y destino fuera del webroot.
- Actualizar el kernel y aplicar parches de seguridad.
- Retirar binarios SUID innecesarios como el helper de S-nail.
- Alertar de consultas GraphQL de introspección, subidas PHP y ejecución de exploits de kernel.

## Referencias

- [0xdf — Help](https://0xdf.gitlab.io/2019/06/08/htb-help.html)
- [IppSec — Help](https://www.youtube.com/watch?v=XB8CbhfOczU)
- [Hack The Box — Help](https://app.hackthebox.com/machines/help)
- [NVD — CVE-2017-16995](https://nvd.nist.gov/vuln/detail/CVE-2017-16995)
- [NVD — CVE-2017-5899](https://nvd.nist.gov/vuln/detail/CVE-2017-5899)
- [Knowledge — Elevación con CVE-2017-16995](../../../knowledge/linux/kernel-cve-2017-16995.md)
