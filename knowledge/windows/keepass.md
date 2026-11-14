---
topic: KeePass
tags: [windows, keepass, kdbx, password-manager, hashcat, key-file]
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

## Referencias

- <https://keepass.info/help/base/security.html>
- <https://github.com/openwall/john>
- <https://attack.mitre.org/techniques/T1555/005/>
