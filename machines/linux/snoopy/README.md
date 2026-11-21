---
machine: Snoopy
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, dns, bind, mattermost, git-apply, cve-2023-23946, clamav, cve-2023-20052, privesc]
---

# Snoopy — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`download?file=` tiene directory traversal; se lee la configuración de BIND y sus claves TSIG, se actualiza la zona DNS y se redirigen los correos de restablecimiento de `snoopy.htb` a un servidor propio. Eso da acceso a Mattermost; un slash command que aprovisiona servidores se apunta a un honeypot SSH y entrega credenciales de `cbrown`. `cbrown` puede ejecutar `git apply -v` como `sbrown` con una regex muy restrictiva; la CVE-2023-23946 permite escribir fuera del repositorio mediante un symlink creado por el propio parche y llegar a `sbrown`. Para root, `sudo` permite `clamscan --debug` sobre un directorio concreto; se explota la CVE-2023-20052 (XXE al parsear DMG) para ejecutar como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,53,80 <IP>
```

- `22`: OpenSSH 8.9p1 Ubuntu.
- `53`: ISC BIND 9.18.12.
- `80`: nginx 1.18.0.

```bash
echo '<IP> snoopy.htb mattermost.snoopy.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://snoopy.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El sitio tiene descargas con `download?file=`. Un wordlist de LFI confirma traversal con secuencias `....//`; se lee `/etc/passwd` y la configuración de BIND (`/etc/bind/named.conf.local` y las claves). También se descubre el vhost de Mattermost y el dominio de correo.

La zona DNS permite actualizaciones con las claves TSIG leídas. Se añade un registro MX o se cambia el destino del correo de restablecimiento para que llegue a un servidor propio.

```bash
python3 -m aiosmtpd -n -l 0.0.0.0:25
nsupdate -k <TSIG_KEY>
```

## Foothold

Se solicita el restablecimiento de contraseña de una cuenta de Mattermost y el correo llega al servidor propio. El enlace permite cambiar la contraseña y entrar en Mattermost. Dentro hay un slash command que aprovisiona servidores: se configura para que se conecte a un honeypot SSH (Cowrie) propio. El comando envía credenciales al honeypot, que las registra; son las de `cbrown`.

## Movimiento lateral

`cbrown` puede ejecutar como `sbrown` un único comando:

```text
(sbrown) PASSWD: /usr/bin/git ^apply -v [a-zA-Z0-9.]+$
```

La regex no permite espacios, así que el parche debe ser un solo argumento. Git 2.34.1 es vulnerable a CVE-2023-23946: un parche puede crear un symlink y escribir a través de él fuera del repositorio. Se prepara un parche que crea el enlace y escribe en `/home/sbrown/.ssh/authorized_keys`, y se aplica con `sudo -u sbrown git apply -v <parche>`.

## Escalada de privilegios

`sbrown` puede ejecutar como root:

```text
(root) NOPASSWD: /usr/local/bin/clamscan ^--debug /home/sbrown/scanfiles/[a-zA-Z0-9.]+$
```

ClamAV 1.0.0 es vulnerable a CVE-2023-20052: el parser de DMG procesa XML sin deshabilitar entidades externas, lo que permite un XXE. Se coloca un `.dmg` manipulado en `scanfiles` y se ejecuta `clamscan`; la entidad externa lee la clave SSH de root.

```bash
sudo /usr/local/bin/clamscan --debug /home/sbrown/scanfiles/<FILE>.dmg
```

CVE-2023-20032 (desbordamiento en HFS+) se menciona en la documentación de la máquina, pero no se explota.

## Evidencia

- Traversal en `download?file=` y lectura de la configuración de BIND.
- Claves TSIG y actualización de la zona DNS.
- Correo de restablecimiento recibido y acceso a Mattermost.
- Slash command apuntando al honeypot y credenciales de `cbrown`.
- `sudo -l` con `git apply` y parche de CVE-2023-23946.
- `sudo -l` con `clamscan` y DMG con XXE.
- `id` con UID 0.

## Lecciones aprendidas

- Un LFI permite leer configuración de servicios y claves, no solo `/etc/passwd`.
- Las claves TSIG permiten modificar DNS y desviar correo.
- Los slash commands que aprovisionan servidores pueden enviar credenciales a un destino controlado.
- Una regex en `sudo` no impide explotar una vulnerabilidad del binario.
- ClamAV también procesa formatos de disco y puede ser vulnerable a XXE.
- No hay que confundir las dos CVE de ClamAV: la explotada es la XXE de DMG.

## Mitigaciones y detección

- Validar rutas de descarga y bloquear traversal.
- Proteger las claves TSIG y restringir las actualizaciones DNS.
- Verificar el destino de los correos de restablecimiento y usar tokens de un solo uso.
- Revisar los slash commands y limitar sus destinos de red.
- Actualizar Git y ClamAV; no permitir `git apply` ni `clamscan` con `sudo`.
- Alertar de actualizaciones DNS, correos de reset y escaneos de DMG.

## Referencias

- [0xdf — Snoopy](https://0xdf.gitlab.io/2023/09/23/htb-snoopy.html)
- [IppSec — Snoopy](https://www.youtube.com/watch?v=6tn30O0SjVQ)
- [Hack The Box — Snoopy](https://app.hackthebox.com/machines/snoopy)
- [NVD — CVE-2023-23946](https://nvd.nist.gov/vuln/detail/CVE-2023-23946)
- [NVD — CVE-2023-20052](https://nvd.nist.gov/vuln/detail/CVE-2023-20052)
- [Knowledge — git apply y CVE-2023-23946](../../../knowledge/linux/git-apply-cve-2023-23946.md)
