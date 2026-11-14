---
topic: NTLM authentication
tags: [windows, ntlm, netntlmv2, relay, pass-the-hash, authentication]
---

# NTLM authentication

[🌐 English](ntlm-authentication.en.md) | **Español**

## Concepto

NTLM autentica mediante un reto y una respuesta derivada de la contraseña. El servidor no recibe la contraseña, pero un atacante puede capturar el reto/respuesta, relayarlo a otro servicio o usar el hash NTLM directamente si conoce el valor.

## Cuándo aplica

- SMB, LDAP, HTTP o MSSQL con NTLM.
- SMB signing deshabilitado.
- Captura de tráfico interno.
- Credenciales en formato hash.

## Procedimiento

1. Identificar servicios que aceptan NTLM.
2. Comprobar la firma SMB.
3. Capturar o relayar una autenticación.
4. Usar el hash para Pass-the-Hash.
5. Crackear NetNTLMv2 si no se puede relayar.

```bash
nxc smb <HOST> -u <USER> -p '<PASSWORD>' --shares
responder -I <IFACE> -wv
impacket-ntlmrelayx -tf targets.txt -smb2support
hashcat -m 5600 hashes.txt wordlist.txt
```

## Variantes

- NetNTLMv2 capturado y crackeado.
- Relay a SMB, LDAP o MSSQL.
- Pass-the-Hash con NTLM.
- Coerción de autenticación con PetitPotam o PrinterBug.

## Limitaciones

- SMB signing bloquea el relay.
- El hash debe ser válido y tener permisos.
- La segmentación limita el movimiento.
- Las políticas de autenticación pueden requerir Kerberos.

## Mitigación y detección

- Habilitar SMB signing y LDAP signing.
- Deshabilitar NTLM cuando sea posible.
- Aplicar segmentación y LAPS.
- Alertar de autenticaciones relayadas y hashes usados.

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview>
- <https://attack.mitre.org/techniques/T1550/002/>
- <https://github.com/lgandx/Responder>
