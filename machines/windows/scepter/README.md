---
machine: Scepter
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, nfs, adcs, esc14, dcsync]
---

# Scepter — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un recurso NFS sin autenticación expone certificados PFX. Con uno se obtiene acceso al dominio; permisos para cambiar contraseñas y dos variantes de AD CS ESC14 llevan a DCSync y al control del dominio.

## Reconocimiento

```bash
nmap -Pn -sCV -p111,2049,88,389,445 <IP>
showmount -e <IP>
mount -t nfs <IP>:/export /mnt/nfs
# AD CS
certipy find -u <USER>@<DOMAIN> -p "<PASS>" -dc-ip <DC> -vulnerable
certipy auth -pfx <CERT>.pfx -dc-ip <DC>
bloodyAD --host <DC> -d <DOMAIN> -u <USER> -p "<PASS>" set password <TARGET> "<NEWPASS>"
```

## Enumeración

- NFS exportado sin autenticación con archivos PFX.
- Active Directory con AD CS y `altSecurityIdentities` manipulables.
- Permisos para cambiar la contraseña de otro usuario.

## Acceso inicial

Se monta el recurso NFS y se recuperan los PFX. `certipy auth` usa el certificado para obtener un TGT; con la cuenta resultante se enumeran permisos y se identifica la ruta de AD CS.

## Escalada de privilegios

Se cambia la contraseña de un usuario con permisos de escritura y se obtiene su contexto. ESC14 permite mapear un certificado a una cuenta privilegiada mediante `altSecurityIdentities`; se solicita el certificado y se usa para DCSync.

## Evidencia

- PFX recuperado del NFS.
- TGT emitido con `certipy auth`.
- Certificado ESC14 y volcado DCSync.

## Lecciones aprendidas

- NFS sin autenticación puede exponer material criptográfico.
- AD CS debe auditarse más allá de ESC1–ESC8.
- `altSecurityIdentities` mal gestionado rompe el modelo de confianza.

## Mitigación y detección

- Restringir exports NFS y proteger PFX.
- Auditar plantillas, permisos y `altSecurityIdentities`.
- Aplicar mínimo privilegio sobre cambios de contraseña.

## Referencias

- [0xdf — Scepter](https://0xdf.gitlab.io/2025/07/19/htb-scepter.html)
- [SpecterOps — ESC14](https://posts.specterops.io/adcs-esc14-abuse-14d1a58b8b5a)
- [Hack The Box — Scepter](https://app.hackthebox.com/machines/scepter)
