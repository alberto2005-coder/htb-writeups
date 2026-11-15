---
title: ADIDNS — secuestro de nombres con CREATE_CHILD
tags: [windows, active-directory, dns, adidns, responder, mitm]
---

# ADIDNS — secuestro de nombres con CREATE_CHILD

[🇬🇧 English](adidns-record-spoofing.en.md) | **Español**

## Concepto

Las zonas DNS integradas en Active Directory se guardan como objetos en el directorio. Por defecto, los usuarios autenticados pueden crear registros hijos (`CREATE_CHILD`) en muchos nombres. Si un servicio intenta resolver un nombre que aún no existe, un atacante puede crearlo apuntando a su propia IP y quedarse con la resolución.

## Cuándo aplica

- Hay un bosque AD con DNS integrado.
- Un linked server, una aplicación o un script resuelve un nombre inexistente.
- El usuario comprometido puede crear registros en la zona.

## Procedimiento

1. Enumerar la zona y los permisos con `Powermad` o `dnstool.py`.
2. Identificar un nombre que la víctima intenta resolver y que no existe.
3. Crear un registro A hacia la IP del atacante.
4. Escuchar con Responder o un servidor propio y capturar la autenticación.

```powershell
Import-Module .\Powermad.ps1
Get-ADIDNSNode -DomainController dc.htb -Zone htb
New-ADIDNSNode -DomainController dc.htb -Zone htb -Node fake -Data 10.10.14.9 -Type A
```

```bash
python3 dnstool.py -u 'HTB\user' -p '<PASSWORD>' -r fake.htb -a add -t A -d 10.10.14.9 dc.htb
```

## Variantes

- Crear un registro comodín (`*`) para capturar cualquier nombre no resuelto.
- Usar `TXT` o `CNAME` para redirigir a otro host.
- Combinar con ` PetitPotam` o un `xp_dirtree` para forzar la autenticación.

## Limitaciones

- El permiso `CREATE_CHILD` debe existir; suele estar en `Authenticated Users`, pero no siempre.
- La víctima debe resolver el nombre después de crearlo.
- Responder solo captura protocolos legados (LLMNR, NBT-NS, mDNS); para SMB se necesita relay o un servidor falso.

## Mitigación y detección

- Restringir `CREATE_CHILD` en zonas y nombres sensibles.
- Auditar eventos 5137, 5141 y cambios de registros DNS.
- Usar DNS firmado y monitorear registros nuevos que apunten a IPs externas.
- Evitar que servicios internos resuelvan nombres no existentes.

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-zones-records>
- <https://github.com/Kevin-Robertson/Powermad>
- <https://attack.mitre.org/techniques/T1557/>
