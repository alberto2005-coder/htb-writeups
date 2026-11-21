---
topic: Active Directory — Get-bADpasswords, certificados y DCSync
tags: [windows, active-directory, dcsync, certificado, firma-de-codigo, kerberos, hathor]
---

# Active Directory — Get-bADpasswords, certificados y DCSync

[🌐 English](badpasswords-dcsync.en.md) | **Español**

## Concepto

`Get-bADpasswords` es una herramienta que audita contraseñas débiles en Active Directory y necesita permisos de replicación (DCSync) para leer hashes. Si una tarea privilegiada ejecuta un script modificable y firmado con un certificado válido, se puede conseguir que esa cuenta ejecute código. En Hathor, un certificado de firma recuperado de la papelera permitió modificar el script y ejecutarlo como `bpassrunner`; después se hizo DCSync y, como NTLM estaba deshabilitado, se usaron tickets Kerberos.

## Cuándo aplica

- Una tarea programada ejecuta un script de auditoría como usuario privilegiado.
- El script es modificable o se puede reemplazar.
- Hay un certificado de firma de código disponible (papelera, shares, backups).
- La cuenta tiene permisos de replicación o se puede obtener un ticket.

## Procedimiento

1. Localizar la tarea, el script y el usuario que lo ejecuta.
2. Comprobar si el script está firmado y si la firma se valida.
3. Obtener un certificado de firma y su clave.
4. Modificar el script y firmarlo de nuevo.
5. Esperar la ejecución programada y obtener ejecución como la cuenta.
6. Ejecutar DCSync y usar el hash o un ticket Kerberos.

## Comandos

```powershell
Get-ScheduledTask | Where-Object { $_.Actions.Execute -match 'powershell|vbs|cmd' }
Get-AuthenticodeSignature C:\Get-bADpasswords\run.vbs
```

```powershell
Get-ADReplAccount -SamAccountName administrator -Server '<DC>'
```

```bash
getTGT.py -hashes :<NTHASH> <DOMAIN>/administrator
KRB5CCNAME=./administrator.ccache evil-winrm -i <DC> -r <DOMAIN>
```

## Variantes

- Sustituir el script por un binario o un `.lnk` si la tarea lo permite.
- Usar `signtool` con un certificado exportable y su contraseña.
- DCSync con `mimikatz` (`lsadump::dcsync`) en lugar de `Get-ADReplAccount`.
- Pass-the-hash si NTLM está habilitado.
- `gettgt`/`getST` para obtener tickets con el hash.

## Limitaciones

- La firma debe ser válida y el certificado debe estar vigente.
- La tarea puede ejecutarse con una cuenta sin permisos de replicación.
- DCSync requiere derechos de replicación o privilegios de dominio.
- NTLM deshabilitado impide el uso directo del hash.
- La modificación del script puede quedar registrada.

## Mitigación

- Proteger los scripts de auditoría con permisos de solo lectura.
- Validar la firma y el editor en las tareas programadas.
- Retirar certificados de firma de papelera, shares y backups.
- Limitar los permisos de replicación a cuentas concretas.
- Auditar DCSync y el uso de tickets Kerberos.

## Detección

- Scripts firmados modificados o con firma inválida.
- Ejecución de `Get-bADpasswords` fuera de la ventana habitual.
- DCSync desde hosts que no son controladores.
- Solicitudes de ticket para cuentas privilegiadas.
- Certificados de firma usados después de su retirada.

## Referencias

- [0xdf — Hathor](https://0xdf.gitlab.io/2022/11/19/htb-hathor.html)
- [GitHub — Get-bADpasswords](https://github.com/malteposener/Get-bADpasswords)
- [MITRE — DCSync](https://attack.mitre.org/techniques/T1003/006/)
- [Ficha Hathor](../../machines/windows/hathor/README.md)
