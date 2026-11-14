---
topic: NTDS extraction
tags: [windows, active-directory, ntds, secretsdump, dcsync, credentials]
---

# NTDS extraction

[🌐 English](ntds-extraction.en.md) | **Español**

## Concepto

`NTDS.dit` es la base de Active Directory y contiene hashes de cuentas de dominio. Se puede extraer de un controlador de dominio con una copia de volumen, acceso administrativo o DCSync, y combinarla con el hive `SYSTEM` para descifrar los hashes.

## Cuándo aplica

- Controlador de dominio comprometido.
- Derechos de replicación o DCSync.
- Copia de seguridad del DC.
- Acceso administrativo al disco.

## Procedimiento

1. Confirmar privilegios sobre el DC.
2. Crear una copia de `NTDS.dit` o usar DCSync.
3. Obtener el hive `SYSTEM`.
4. Extraer hashes con `secretsdump`.
5. Reutilizar o crackear los hashes.

```bash
impacket-secretsdump -ntds NTDS.dit -system SYSTEM LOCAL
impacket-secretsdump <DOMAIN>/<USER>:'<PASSWORD>'@<DC> -just-dc
vssadmin create shadow /for=C:
```

## Variantes

- DCSync con derechos de replicación.
- Copia con `ntdsutil` o VSS.
- Extracción desde un backup.
- Volcado de hashes de cuentas de servicio.

## Limitaciones

- Se requieren privilegios elevados.
- El antivirus puede detectar `secretsdump`.
- La copia puede ser bloqueada por el DC.
- Los hashes pueden requerir cracking.

## Mitigación y detección

- Restringir derechos de replicación.
- Proteger backups y el acceso físico.
- Monitorizar DCSync (4662) y copias de VSS.
- Rotar credenciales tras una exposición.

## Referencias

- <https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/jj574173(v=ws.11)>
- <https://attack.mitre.org/techniques/T1003/003/>
- <https://github.com/fortra/impacket>
