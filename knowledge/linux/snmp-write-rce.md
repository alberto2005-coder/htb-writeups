---
topic: SNMP — comunidad de escritura y ejecución remota
tags: [linux, snmp, net-snmp, rce, privesc]
---

# SNMP — comunidad de escritura y ejecución remota

[🌐 English](snmp-write-rce.en.md) | **Español**

## Concepto

Una comunidad SNMP con permisos de escritura permite modificar la configuración de `snmpd`, incluida la extensión `nsExtendOutput1Line`, que ejecuta comandos como el usuario del demonio. También se pueden cambiar rutas y scripts de monitorización.

## Cuándo aplica

- SNMP responde con una comunidad válida.
- La comunidad tiene permisos `rw` sobre `NET-SNMP-EXTEND-MIB`.
- El demonio corre con privilegios útiles.

## Procedimiento

1. Enumerar comunidades con `onesixtyone` o `snmpwalk`.
2. Comprobar escritura en `nsExtend`.
3. Crear una extensión que ejecute una reverse shell.
4. Leer la salida con `nsExtendOutput1Line`.

## Comandos

```bash
onesixtyone -c communities.txt <IP>
snmpwalk -v2c -c <COMMUNITY> <IP> NET-SNMP-EXTEND-MIB::nsExtendObjects
snmpset -v2c -c <COMMUNITY> <IP> NET-SNMP-EXTEND-MIB::nsExtendCommand."pwn" s "/bin/bash"
```

## Variantes

- Usar `snmp-shell` para automatizar.
- Modificar `nsExtendInput` para pasar comandos.
- Escribir en un script de monitorización.

## Limitaciones

- La comunidad puede ser solo lectura.
- `snmpd` puede correr como usuario sin shell.
- La extensión requiere reinicio en algunas versiones.

## Mitigación

- Usar SNMPv3 con autenticación y solo lectura.
- No exponer UDP/161 a Internet.
- Ejecutar `snmpd` con mínimo privilegio.

## Detección

- `snmpset` sobre `nsExtend`.
- Nuevas extensiones o procesos hijos de `snmpd`.
- Consultas SNMP desde hosts no autorizados.

## Referencias

- [Net-SNMP — extend MIB](https://www.net-snmp.org/docs/mibs/NET-SNMP-EXTEND-MIB.txt)
- [0xdf — Intense](https://0xdf.gitlab.io/2020/11/14/htb-intense.html)
- [HackTricks — SNMP](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-snmp/index.html)
