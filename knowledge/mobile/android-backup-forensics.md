---
topic: Android backup forensics
tags: [mobile, android, adb, backup, sqlite, data-extraction]
---

# Android backup forensics

[🌐 English](android-backup-forensics.en.md) | **Español**

## Concepto

Android permite exportar los datos de una aplicación mediante `adb backup` cuando el manifiesto declara `android:allowBackup="true"`. El resultado es un archivo `.ab` con cabecera propia y un payload comprimido que contiene el directorio privado de la app. Es una fuente habitual en análisis forense y en retos Mobile.

## Cuándo aplica

- Extracción de datos de una app sin root.
- Análisis de una copia de seguridad `.ab`.
- Revisión de `allowBackup` y de datos sensibles.
- Retos con SQLite, preferencias o bases locales.

## Requisitos y condiciones

- ADB y un dispositivo o emulador con la app instalada.
- El APK o la copia `.ab` original.
- Herramienta `abe` o equivalente para desempaquetar.
- Espacio para extraer el TAR y analizarlo.

## Procedimiento

1. Comprobar `allowBackup` en `AndroidManifest.xml`.
2. Generar la copia con `adb backup` o recibir el `.ab`.
3. Convertir el `.ab` a TAR.
4. Extraer y localizar bases SQLite, preferencias y cachés.
5. Consultar las tablas y buscar cadenas relevantes.

```bash
adb backup -apk -shared -all -f backup.ab
java -jar abe.jar unpack backup.ab backup.tar
tar xf backup.tar
find . -iname '*.db' -o -iname '*.sqlite' -o -iname '*.xml'
```

## Variantes

- Backup completo del dispositivo.
- Backup de una sola app.
- Copia lógica mediante `run-as` en builds debug.
- Extracción física con acceso root o imagen de usuario.

## Limitaciones

- `allowBackup=false` impide la copia lógica.
- Algunas apps cifran la base o usan un almacén de claves.
- El backup puede no incluir archivos en caché externa.
- La versión de Android y el fabricante cambian el formato.

## Mitigación

- Desactivar `allowBackup` o excluir datos sensibles.
- Cifrar bases y secretos con Android Keystore.
- No guardar credenciales en texto plano.
- Auditar backups en dispositivos corporativos.

## Detección

- Alertar de ejecuciones de `adb backup` en flotas gestionadas.
- Revisar cambios en `allowBackup` durante el build.
- Monitorizar acceso físico y depuración USB.
- Comparar el inventario de datos con la política de retención.

## Referencias

- <https://developer.android.com/guide/topics/data/autobackup>
- <https://developer.android.com/tools/adb#backup>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1409/>
