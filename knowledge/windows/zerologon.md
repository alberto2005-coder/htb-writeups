---
topic: ZeroLogon (CVE-2020-1472)
tags: [windows, active-directory, zerologon, netlogon, cve-2020-1472]
---

# ZeroLogon (CVE-2020-1472)

[🇬🇧 English](zerologon.en.md) | **Español**

## Concepto

ZeroLogon es una vulnerabilidad crítica en el protocolo Netlogon. El uso de AES-CFB8 con un IV de ceros permite a un atacante autenticarse como una cuenta de equipo sin conocer su contraseña. El objetivo habitual es un controlador de dominio: se restablece la contraseña de la cuenta de equipo del DC y se obtiene acceso para volcar credenciales.

## Cuándo aplica

- DC sin el parche de agosto de 2020.
- Netlogon accesible desde la red del atacante.
- El dominio no tiene enforcement de modo seguro.
- Se busca un compromiso total del dominio.

## Requisitos y condiciones

1. Conectividad con el DC (RPC/Netlogon).
2. Nombre del DC y su cuenta de equipo.
3. Herramienta de explotación (`zerologon`, Mimikatz, impacket).
4. Capacidad de restaurar la contraseña original para no romper el dominio.

## Procedimiento

Se prueba el bypass:

```bash
python3 zerologon.py <DC_NAME> <DC_IP>
```

Si tiene éxito, la contraseña de la cuenta de equipo queda vacía. Se vuelca el hash de Administrator:

```bash
impacket-secretsdump -just-dc -hashes :<NTLM_HASH> administrator@<DC_IP>
```

Se usa el hash para `psexec`/`wmiexec`. En un laboratorio, se restaura la contraseña original con el script de restauración o `netdom` para evitar romper la confianza.

## Variantes

- **Mimikatz**: `lsadump::zerologon` y `lsadump::dcsync`.
- **Impacket**: módulos de Netlogon y secretsdump.
- **Ataque encadenado**: ZeroLogon para resetear, DCSync para volcar.
- **DCSync directo**: si ya se tiene un usuario con derechos, no hace falta ZeroLogon.

## Limitaciones

- Microsoft parcheó la vulnerabilidad y añadió enforcement.
- El ataque es destructivo: cambiar la contraseña del DC puede romper la replicación.
- Los DC modernos y los dominios con `FullSecureChannelProtection` no son vulnerables.
- Requiere que Netlogon acepte el canal inseguro.

## Mitigación

- Aplicar el parche de CVE-2020-1472.
- Habilitar enforcement (`FullSecureChannelProtection`).
- Segmentar DCs y restringir Netlogon.
- Monitorizar cambios de contraseña de cuentas de equipo.
- Tener un procedimiento de restauración documentado.

## Detección

- Evento 4742 (cuenta de equipo modificada) fuera de ventana.
- Autenticaciones Netlogon anómalas y errores repetidos.
- Cambios de contraseña de la cuenta del DC.
- Tráfico RPC/Netlogon desde hosts no administrativos.
- Eventos de restauración de contraseña y fallos de replicación.

MITRE ATT&CK: T1068 (Exploitation for Privilege Escalation), T1003.006 (DCSync).

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2020-1472>
- <https://www.secura.com/blog/zero-logon>
- <https://attack.mitre.org/techniques/T1068/>
