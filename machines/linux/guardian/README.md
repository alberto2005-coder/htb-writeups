---
machine: Guardian
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, php, gitea, phpspreadsheet, csrf, lfi, privesc]
---

# Guardian — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El portal universitario tiene un IDOR en el chat que filtra la contraseña de Gitea de un profesor. El repositorio revela un PhpSpreadsheet vulnerable: un XLSX malicioso ejecuta XSS y roba la sesión del lecturer. Un CSRF con token débil permite crear un administrador; como admin, un LFI con `php://filter` da RCE y `www-data`. El hash de la base se crackea y la contraseña se reutiliza en `jamil`, que puede ejecutar `utilities.py` como `mark`. `safeapache2ctl` permite leer archivos de root y cargar un módulo para obtener una shell SUID.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,3000 <IP>
```

- `80/443` sirven `guardian.htb` y `portal.guardian.htb`.
- `ffuf` encuentra `gitea.guardian.htb` y `admin.guardian.htb`.
- El portal permite registrarse como estudiante y usar un chat.

## Enumeración

- El chat usa `chat_users[0]` y `chat_users[1]`; cambiar los IDs muestra conversaciones ajenas (IDOR).
- Un mensaje del administrador entrega la contraseña de Gitea de `jamil.enockson`.
- El repositorio `portal.guardian.htb` contiene el código y la versión de PhpSpreadsheet.

## Foothold

La carga de notas usa PhpSpreadsheet y acepta XLSX. Una hoja con una fórmula maliciosa ejecuta XSS cuando el lecturer abre el archivo; la cookie robada da acceso a su cuenta. Un CSRF con un token predecible permite crear un usuario admin.

```text
http://portal.guardian.htb/student/chat.php?chat_users[0]=1&chat_users[1]=2
```

## Movimiento lateral

Como admin, `admin/reports.php` incluye el parámetro `report` y permite `php://filter`. Una cadena de conversión escribe un webshell y da `www-data`. El hash de la base se crackea y la contraseña funciona por SSH para `jamil`.

```bash
ssh jamil@guardian.htb
```

`jamil` puede ejecutar `/opt/scripts/utilities/utilities.py` como `mark`; `utils/status.py` es escribible por el grupo y se modifica para ejecutar una shell como `mark`.

## Escalada de privilegios

`mark` ejecuta `safeapache2ctl` con una configuración propia. La opción `-f` permite un `Include /root/root.txt` para leer la flag, y `LoadModule` carga un `.so` que crea una copia SUID de bash antes de fallar.

```bash
printf 'LoadModule evil /home/mark/confs/evil.so\n' > /home/mark/confs/0xdf.conf
safeapache2ctl -f /home/mark/confs/0xdf.conf
/tmp/0xdf -p
```

## Evidencia

- IDOR en el chat y contraseña de Gitea.
- XLSX con XSS y sesión de lecturer.
- CSRF y creación de admin.
- LFI con filter chain y `www-data`.
- Hash crackeado, `utilities.py` y `safeapache2ctl`.

## Lecciones aprendidas

- Un IDOR en un chat filtra conversaciones y credenciales.
- Procesar archivos de usuario con PhpSpreadsheet expone XSS y más.
- Un wrapper de Apache que acepta `-f` y módulos del usuario es root.

## Mitigación y detección

- Validar el usuario de la sesión en cada chat y no confiar en IDs.
- Actualizar PhpSpreadsheet y aislar la carga de documentos.
- Usar tokens CSRF fuertes y no permitir `Include`/`LoadModule` en configuraciones de usuario.
- Ejecutar `utilities.py` con permisos mínimos y revisar los scripts escribibles.

## Referencias

- [0xdf — Guardian](https://0xdf.gitlab.io/2026/02/28/htb-guardian.html)
- [IppSec — Guardian](https://www.youtube.com/watch?v=Fzt-oZX0Mzo)
- [Hack The Box — Guardian](https://app.hackthebox.com/machines/guardian)
