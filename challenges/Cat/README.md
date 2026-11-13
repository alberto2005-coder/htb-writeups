---
challenge: Cat
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, adb-backup, sqlite, data-extraction]
---

# Cat — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app guarda datos en una base SQLite y permite copias de seguridad mediante `adb backup`. El archivo `.ab` se convierte a TAR, se extrae y la base revela la flag.

## Enunciado y superficie

- Mobile, Easy, retirado.
- Se entrega un APK y, según el enunciado, una copia de seguridad Android.
- La app almacena información local.

```bash
file cat.apk backup.ab
```

## Reconocimiento

- `AndroidManifest.xml` declara `android:allowBackup="true"`.
- La app no requiere root para exportar sus datos.
- El backup contiene el directorio privado de la aplicación.

```bash
apktool d cat.apk -o apk
grep -RIn 'allowBackup\|databases\|sqlite' apk/AndroidManifest.xml apk/res 2>/dev/null | head
```

## Análisis

El formato `.ab` tiene cabecera propia y payload comprimido. `abe` lo convierte a TAR; después se extrae el directorio de la app y se localiza la base de datos.

```bash
java -jar abe.jar unpack backup.ab backup.tar
tar xf backup.tar
find . -iname '*.db' -o -iname '*.sqlite'
```

## Explotación

1. Convertir el backup a TAR.
2. Extraer el contenido en un directorio de trabajo.
3. Abrir la base SQLite y listar tablas.
4. Buscar la flag en las columnas de texto.

```bash
sqlite3 apps/<PACKAGE>/db/<DB> '.tables'
sqlite3 apps/<PACKAGE>/db/<DB> "select * from <TABLE>;"
```

Si el backup no está disponible, se puede generar desde un emulador con la app instalada y `adb backup -apk -shared -all`.

## Evidencia

- Cabecera del `.ab` y conversión a TAR.
- Ruta de la base dentro del backup.
- Consulta SQL con la flag redactada.

## Lecciones aprendidas

- `allowBackup` expone datos privados sin root.
- Un backup es una copia completa del directorio de la app.
- SQLite es fácil de inspeccionar una vez extraído.

## Mitigaciones y detección

- Desactivar `allowBackup` o excluir datos sensibles.
- Cifrar la base y derivar claves de un almacén seguro.
- No guardar secretos en texto plano.
- Auditar backups y accesos ADB en dispositivos corporativos.

## Referencias

- <https://www.hackthebox.com/challenges/Cat>
- <https://developer.android.com/guide/topics/data/autobackup>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1409/>
