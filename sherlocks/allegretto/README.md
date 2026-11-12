---
sherlock: Allegretto
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, bitlocker, ewf, registry, thunderbird, usb]
---

# Allegretto — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin evidencia original ni respuestas literales.

## TL;DR

Investigación de un equipo incautado a un sospechoso. La imagen EWF está protegida con BitLocker; la clave de recuperación aparece en los documentos del usuario. Dentro se analizan NTUSER.DAT/SOFTWARE con RECmd, el perfil de Thunderbird y la papelera, donde un KML eliminado revela coordenadas.

## Escenario

La policía incauta el equipo de un supuesto traficante que usa la dark web y almacenamiento cifrado. Se solicita reconstruir identidades, correos, ubicaciones y actividad delictiva a partir de los artefactos.

## Artefactos

- Imagen forense en formato EWF.
- Volumen BitLocker y clave de recuperación en documentos.
- Hives `NTUSER.DAT` y `SOFTWARE`.
- Perfil de Thunderbird (`prefs.js`, `ImapMail`, `Local Folders`).
- Imagen USB y papelera de reciclaje.

## Metodología

1. Se monta la imagen EWF con `ewfmount` y se identifica el volumen BitLocker.
2. Se usa `dissect.fve` o una herramienta equivalente para descifrar con la clave de recuperación.
3. Se monta el NTFS con `dissect.ntfs` o `ntfs-3g`.
4. Se procesan los hives con `RECmd` y un batch file; se revisan ejecuciones, USB y aplicaciones.
5. Se parsea Thunderbird: cuentas en `prefs.js`, correos en `ImapMail` y contactos.
6. Se revisa la papelera (`$R`/`$I`) y se recupera el KML eliminado con coordenadas.

```bash
ewfmount evidence.E01 /mnt/ewf
dissect.fve /mnt/ewf/ewf1 /mnt/bitlocker --recovery-key <KEY>
```

## Preguntas tipo

- ¿Qué identidad usa el sospechoso en la dark web?
- ¿Cuál es su correo de contacto?
- ¿Qué aplicación de correo y qué cuentas configuró?
- ¿Qué archivo eliminado contenía la ubicación?
- ¿Qué coordenadas revela el KML?

## Herramientas

`ewfmount`, `dissect.fve`, `dissect.ntfs`, `RECmd`, `DB Browser for SQLite`, `unzip`.

## Evidencia y redacción

Se conservan capturas de los hives, del perfil de Thunderbird y de la papelera, con direcciones, correos y coordenadas redactados. No se publican respuestas literales.

## Lecciones aprendidas

- La clave de recuperación puede estar en el propio equipo.
- BitLocker no impide el análisis si se localiza la clave.
- Thunderbird conserva cuentas y correos en texto claro.
- La papelera y los metadatos de USB son fuentes clave.

## Detección

- Monitorizar la creación de imágenes y montajes forenses en equipos corporativos.
- Auditar el acceso a claves de recuperación BitLocker.
- Vigilar exportaciones masivas de perfiles de correo.
- Restringir el uso de USB no cifrados.

## Referencias

- <https://app.hackthebox.com/sherlocks/Allegretto>
- <https://learn.microsoft.com/en-us/windows/security/information-protection/bitlocker/>
- <https://github.com/fox-it/dissect>
