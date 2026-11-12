---
topic: "Entra ID y Sentinel: inicios de sesión, auditoría y KQL"
tags: [cloud, azure, entra-id, sentinel, kql, identity, dfir]
---

# Entra ID y Sentinel: inicios de sesión, auditoría y KQL

[🇬🇧 English](entra-id-sentinel.en.md) | **Español**

> Nota reutilizable. Sin datos de un tenant concreto.

## Idea

Microsoft Entra ID (antes Azure AD) deja dos flujos de registro que resuelven casi cualquier investigación de identidad: **inicios de sesión** y **auditoría del directorio**. Cuando el tenant exporta su diagnóstico a un workspace de Log Analytics, Sentinel los consulta como `SigninLogs` y `AuditLogs`; el resto del trabajo es KQL y contexto.

La diferencia importante: `SigninLogs` dice *quién intentó entrar y qué pasó*; `AuditLogs` dice *qué se cambió en el directorio*. Un compromiso suele necesitar las dos tablas.

## Tablas y columnas

### `SigninLogs`

| Columna | Uso |
|---|---|
| `TimeGenerated` | Línea temporal (UTC) |
| `UserPrincipalName` | Identidad que inicia sesión |
| `ResultType` | Código de error; `0` es éxito |
| `ResultDescription` | Texto del fallo |
| `IPAddress` | Origen de la petición |
| `Location` / `LocationDetails` | País (dos letras) y detalle con ciudad |
| `AppDisplayName` / `AppId` | Aplicación de destino |
| `DeviceDetail` / `UserAgent` | Dispositivo y cliente |
| `RiskLevelDuringSignIn` / `RiskLevelAggregated` | Riesgo de Identity Protection |
| `AlternateSignInName` | Identificador alternativo (teléfono, proxyAddress…) |

`AADNonInteractiveUserSignInLogs` cubre los inicios no interactivos (tokens de servicio, refresh). `AADRiskyUsers` y `AADUserRiskEvents` requieren Identity Protection.

### `AuditLogs`

| Columna | Uso |
|---|---|
| `TimeGenerated` | Línea temporal |
| `OperationName` | Acción ("Add member to role.", "Consent to application."…) |
| `InitiatedBy` | Quién la ejecuta (usuario, app, IP) |
| `TargetResources` | Objeto afectado |
| `Result` | Éxito o fallo |

## Consultas

```kusto
// fallos agrupados: fuerza bruta o password spray
SigninLogs
| where TimeGenerated > ago(7d)
| where ResultType != "0"
| summarize Fallos = count(), Primer = min(TimeGenerated), Ultimo = max(TimeGenerated)
    by UserPrincipalName, IPAddress, ResultType
| order by Fallos desc

// ubicaciones distintas con éxito: posible viaje imposible
SigninLogs
| where TimeGenerated > ago(7d) and ResultType == "0"
| summarize Paises = dcount(Location), Ubicaciones = make_set(Location, 10) by UserPrincipalName
| where Paises > 1

// éxito después de muchos fallos desde la misma IP
let fallos = SigninLogs
| where TimeGenerated > ago(24h) and ResultType != "0"
| summarize Fallos = count() by IPAddress, UserPrincipalName;
SigninLogs
| where TimeGenerated > ago(24h) and ResultType == "0"
| join kind=inner fallos on IPAddress, UserPrincipalName
| where Fallos >= 10
| project TimeGenerated, UserPrincipalName, IPAddress, AppDisplayName, Fallos

// cambios sensibles del directorio
AuditLogs
| where TimeGenerated > ago(7d)
| where OperationName in ("Add member to role.", "Consent to application.",
    "Add service principal credentials.", "Update user.", "Reset password (by admin)")
| project TimeGenerated, OperationName, InitiatedBy, TargetResources, Result
```

## Códigos de error útiles

| Código | Significado |
|---:|---|
| `0` | Éxito |
| `50126` | Usuario o contraseña inválidos |
| `50074` | Se requiere MFA |
| `50076` | MFA no satisfecha |
| `50105` | Usuario no asignado a la aplicación |
| `53003` | Bloqueado por acceso condicional |
| `65001` | Consentimiento no concedido |

La lista completa está en `https://login.microsoftonline.com/error`; no conviene copiarla entera.

## Límites que cambian la investigación

- **Licencia**: el acceso condicional necesita P1; los campos de riesgo, P2. Sin P2 aparecen como `hidden` o vacíos.
- **Retención**: Log Analytics caduca; si el incidente es antiguo, puede que solo queden los datos exportados a Sentinel o a un storage.
- **Cobertura**: el diagnóstico de Entra ID decide qué se envía. Un tenant sin conexión de `SigninLogs` no tiene nada que consultar.
- **Zona horaria**: `TimeGenerated` va en UTC; las preguntas suelen pedir UTC.

## Detección

- Picos de `50126` desde una IP contra muchas cuentas: password spray.
- Éxito desde un país nuevo justo después de fallos: credenciales válidas obtenidas.
- `50076` repetido seguido de éxito: intento de saltar MFA.
- Altas de credenciales en aplicaciones o consentimientos nuevos: persistencia.
- Roles privilegiados añadidos fuera de ventana: escalada.

MITRE ATT&CK: T1110 (Brute Force), T1078.004 (Cloud Accounts), T1556 (Modify Authentication Process), T1098.001 (Additional Cloud Credentials).

## Referencias

- <https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs>
- <https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs>
- <https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins>
- <https://learn.microsoft.com/en-us/azure/sentinel/connect-azure-active-directory>
