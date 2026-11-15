---
machine: Intelligence
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, ad, dns, responder, gmsa, delegation]
---

# Intelligence — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Los PDFs publicados filtran nombres de usuario y una contraseña por defecto para cuentas nuevas. Tras rociarla, `Tiffany.Molina` accede a SMB y descubre un script que visita cada cinco minutos los DNS `web*` con credenciales. Se crea un registro DNS malicioso, Responder captura el hash de `Ted.Graves`, y su grupo lee la GMSA de `svc_int`. Esa cuenta tiene delegación sobre el DC.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,636,3268,3269,9389 <IP>
```

- `53/tcp` DNS, `88/tcp` Kerberos, `389/tcp` LDAP y `445/tcp` SMB: es un controlador de dominio.
- `80/tcp` IIS con una web corporativa y `/documents/` con PDFs.
- El dominio es `intelligence.htb` y el DC `dc.intelligence.htb`.

## Enumeración

- Los metadatos de los PDFs revelan usuarios como `William.Lee` y `Jose.Williams`.
- El patrón `YYYY-MM-DD-upload.pdf` permite enumerar documentos no enlazados.
- Uno de los PDFs anuncia una contraseña inicial común para empleados nuevos.

## Foothold

Se valida el patrón con `kerbrute` y se rocía la contraseña inicial contra todos los usuarios. `Tiffany.Molina` funciona y da acceso a los shares `Users` e `IT`; en `IT` está `downdetector.ps1`.

```bash
kerbrute userenum --dc <IP> -d intelligence.htb users.txt
crackmapexec smb <IP> -u users.txt -p '<DEFAULT_PASSWORD>' -d intelligence.htb
smbclient -U Tiffany.Molina //<IP>/IT
```

## Movimiento lateral

El script lee registros DNS que empiezan por `web` y hace `Invoke-WebRequest` con las credenciales del usuario que lo ejecuta. Se añade un registro `web-<X>` apuntando al atacante y Responder captura el hash Net-NTLMv2 de `Ted.Graves`. `hashcat -m 5600` lo crackea y `Ted.Graves` pertenece a IT Support, que puede leer la contraseña de `svc_int`.

## Escalada de privilegios

Se extrae la contraseña GMSA de `svc_int` con `gMSADumper` y se usa su hash para pedir un ticket S4U2self/S4U2Proxy con `getST.py`, ya que la cuenta tiene delegación sobre el DC. Después se ejecuta `wmiexec` con el ticket de `administrator`.

```bash
python3 gMSADumper.py -u Ted.Graves -p '<PASSWORD>' -l <IP> -d intelligence.htb
getST.py -dc-ip <IP> -spn www/dc.intelligence.htb -hashes :<HASH> -impersonate administrator intelligence.htb/svc_int
KRB5CCNAME=administrator.ccache wmiexec.py -k -no-pass administrator@dc.intelligence.htb
```

## Evidencia

- PDFs con usuarios y contraseña inicial.
- Sesión SMB como `Tiffany.Molina` y `downdetector.ps1`.
- Hash de `Ted.Graves`, GMSA de `svc_int` y shell como administrator.

## Lecciones aprendidas

- Los metadatos de documentos públicos filtran cuentas y políticas internas.
- Una contraseña inicial compartida permite pulverizar todo el dominio.
- Los registros DNS y los scripts programados pueden enviar credenciales a un host controlado.

## Mitigación y detección

- No usar una contraseña inicial común; forzar cambio y MFA.
- Restringir la creación de registros DNS y monitorizar consultas `web*`.
- Revisar scripts programados que usen credenciales y limitar la delegación.

## Referencias

- [0xdf — Intelligence](https://0xdf.gitlab.io/2021/11/27/htb-intelligence.html)
- [IppSec — Intelligence](https://www.youtube.com/watch?v=Jg_BjkxdtsE)
- [Hack The Box — Intelligence](https://app.hackthebox.com/machines/intelligence)
