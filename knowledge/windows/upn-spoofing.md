---
topic: Active Directory — UPN spoofing entre Windows y Linux
tags: [windows, active-directory, kerberos, upn, sssd, privesc]
---

# Active Directory — UPN spoofing entre Windows y Linux

[🌐 English](upn-spoofing.en.md) | **Español**

## Concepto

Windows y Linux resuelven el `userPrincipalName` de forma distinta. Si se puede escribir el UPN de una cuenta controlada y se pide un TGT con `NT_ENTERPRISE`, un host Linux puede autenticarlo como otra cuenta con el mismo UPN, por ejemplo una cuenta `.adm`.

## Cuándo aplica

- Se controla una cuenta con permiso para modificar su UPN o hay `GenericWrite`.
- Existe una cuenta privilegiada con un UPN conocido.
- El host Linux usa SSSD/Kerberos y `use_fully_qualified_names=False`.

## Procedimiento

1. Enumerar UPN y cuentas `.adm`.
2. Asignar a la cuenta controlada el UPN del admin.
3. Pedir un TGT con `principalType=NT_ENTERPRISE`.
4. Usar el ticket en el host Linux y restaurar el UPN.

## Comandos

```bash
bloodyAD --host dc-01 -d darkcorp.htb -u john.w -p '<PASS>' set object angela.w userPrincipalName angela.w.adm
# solicitar TGT con NT_ENTERPRISE y usar el ccache en el host Linux
klist
```

## Variantes

- Cambiar el UPN de una cuenta con `GenericWrite` sobre otra.
- Combinar con shadow credentials para obtener la contraseña.
- Usar `getTGT.py` o Rubeus con `enterprise`.

## Limitaciones

- El host debe confiar en el UPN para mapear la cuenta.
- Un cleanup revierte el UPN y hay que reaplicarlo.
- Kerberos puede rechazar el ticket si el SPN no coincide.

## Mitigación

- Monitorizar cambios de `userPrincipalName`.
- No usar el UPN como identificador único en Linux.
- Aplicar `use_fully_qualified_names=True` y revisar SSSD.

## Detección

- Cambios de UPN seguidos de un TGT `NT_ENTERPRISE`.
- Autenticaciones Linux con un UPN de admin.
- Eventos 4768/4769 anómalos para la cuenta.

## Referencias

- [0xdf — DarkCorp](https://0xdf.gitlab.io/2025/10/18/htb-darkcorp.html)
- [Pen Test Partners — A broken marriage](https://www.pentestpartners.com/security-blog/a-broken-marriage-abusing-mixed-vendor-kerberos-stacks/)
- [Microsoft — userPrincipalName](https://learn.microsoft.com/en-us/windows/win32/adschema/a-userprincipalname)
