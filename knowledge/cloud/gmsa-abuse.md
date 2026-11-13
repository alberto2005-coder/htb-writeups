---
topic: gMSA abuse
tags: [windows, active-directory, gmsa, kerberos, dacl, credential-access]
---

# gMSA abuse

[🌐 English](gmsa-abuse.en.md) | **Español**

## Concepto

Una group Managed Service Account (gMSA) es una cuenta de servicio cuyo hash NTLM es gestionado por Active Directory y rotado automáticamente. La contraseña se deriva de una clave raíz KDS y puede recuperarse si el atacante controla `msDS-GroupMSAMembership` o un derecho equivalente que permita leerla.

## Cuándo aplica

- Enumeración de cuentas de servicio en un dominio.
- Un usuario no administrador con `WriteProperty` sobre una gMSA.
- Movimiento lateral desde una cuenta de servicio.
- Cadenas con `gMSA_Managers` o `PrincipalsAllowedToRetrieveManagedPassword`.

## Requisitos y condiciones

- Acceso autenticado al dominio.
- Permiso para modificar la membresía de la gMSA o capacidad de leerla.
- Herramientas como `BloodHound`, `certipy`, `impacket` o `netexec`.
- Conectividad con el DC y hora sincronizada.

## Procedimiento

1. Enumerar gMSAs y sus permisos.
2. Identificar quién puede escribir `msDS-GroupMSAMembership`.
3. Añadir la cuenta controlada como principal autorizado.
4. Recuperar el hash NTLM de la gMSA.
5. Usar el hash para Kerberos o para acceder a recursos.

```bash
nxc smb dc01.haze.htb -u <USER> -p '<PASSWORD>' --gmsa
python3 certipy-ad shadow auto -username '<GMSA>$@<DOMAIN>' -hashes :<NTLM> -account <TARGET>
```

## Variantes

- gMSA estándar con KDS root key.
- dMSA en dominios más recientes.
- Abuso mediante `WriteOwner` y `WriteMembers` sobre un grupo intermedio.
- Uso del hash para Pass-the-Hash o solicitud de TGT.

## Limitaciones

- Sin permiso sobre la gMSA no se obtiene la contraseña.
- La rotación invalida el hash después de un tiempo.
- Algunos entornos requieren Kerberos y hora exacta.
- La ruta puede depender de ACL intermedias.

## Mitigación

- Auditar quién puede modificar `msDS-GroupMSAMembership`.
- Limitar `gMSA_Managers` y derechos `WriteProperty`.
- Usar tiering administrativo y estaciones PAW.
- Monitorizar cambios de ACL y de grupos.

## Detección

- Alertar de cambios en `msDS-GroupMSAMembership`.
- Detectar lecturas de gMSA desde hosts no autorizados.
- Revisar eventos 4662 y 5136 sobre objetos de servicio.
- Correlacionar autenticaciones con cuentas de servicio inusuales.

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview>
- <https://adsecurity.org/?p=2011>
- <https://attack.mitre.org/techniques/T1558/003/>
- <https://bloodhound.readthedocs.io/>
