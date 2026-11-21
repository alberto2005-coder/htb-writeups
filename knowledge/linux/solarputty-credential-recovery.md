---
topic: SolarPuTTY — recuperación de credenciales de sesión
tags: [linux, solarputty, credenciales, cifrado, instant, forense]
---

# SolarPuTTY — recuperación de credenciales de sesión

[🌐 English](solarputty-credential-recovery.en.md) | **Español**

## Concepto

SolarPuTTY guarda las sesiones y sus credenciales en un archivo cifrado (`sessions-backup.dat`). El cifrado se deriva de una contraseña maestra; si es débil o se conoce, las credenciales se recuperan con herramientas como `SolarPuttyDecrypt` o `SolarPuttyCracker`. En Instant, el archivo estaba en el home de `shirohige` y la contraseña descifrada era la de root.

## Cuándo aplica

- Hay un `sessions-backup.dat` en un home, share o backup.
- La contraseña maestra es débil o reutilizada.
- Se puede ejecutar una herramienta de descifrado en el host o en el equipo de análisis.
- El archivo no está protegido por un segundo factor.

## Procedimiento

1. Localizar el archivo y confirmar que es de SolarPuTTY.
2. Copiarlo al equipo de análisis.
3. Probar `SolarPuttyCracker` con un diccionario.
4. Alternativamente, usar `SolarPuttyDecrypt` si se conoce la contraseña maestra.
5. Reutilizar las credenciales recuperadas en SSH, RDP u otros servicios.

## Comandos

```bash
file sessions-backup.dat
strings sessions-backup.dat | head
python3 SolarPuttyCracker.py sessions-backup.dat -w /usr/share/wordlists/rockyou.txt
```

```powershell
SolarPuttyDecrypt.exe sessions-backup.dat <MASTER_PASSWORD>
```

## Variantes

- Crackeo con `hashcat` si la herramienta extrae un hash.
- Búsqueda de la contraseña maestra en archivos de configuración o notas.
- Uso de una copia del perfil de SolarPuTTY en `%APPDATA%`.
- Descifrado en un host Windows con la misma versión.
- Reutilización de la contraseña maestra para otros archivos.

## Limitaciones

- Una contraseña maestra fuerte hace inviable el crackeo.
- La herramienta debe coincidir con el formato del archivo.
- El archivo puede estar corrupto o incompleto.
- El descifrado requiere ejecutar código de terceros en un entorno controlado.
- Las credenciales pueden haber caducado.

## Mitigación

- Usar contraseñas maestras largas y únicas.
- Proteger los archivos de sesión con permisos restrictivos.
- No guardar credenciales de root en herramientas de escritorio.
- Rotar credenciales y aplicar MFA en SSH/RDP.
- Cifrar backups y limitar su acceso.

## Detección

- Acceso a `sessions-backup.dat` desde procesos no habituales.
- Copias del archivo fuera del host.
- Intentos de `su` o SSH con credenciales recuperadas.
- Ejecución de `SolarPuttyCracker` o `SolarPuttyDecrypt`.
- Uso de contraseñas de escritorio en cuentas privilegiadas.

## Referencias

- [0xdf — Instant](https://0xdf.gitlab.io/2025/03/01/htb-instant.html)
- [GitHub — SolarPuttyDecrypt](https://github.com/VoidSec/SolarPuttyDecrypt)
- [GitHub — SolarPuttyCracker](https://github.com/ItsWatchMakerr/SolarPuttyCracker)
- [Ficha Instant](../../machines/linux/instant/README.md)
