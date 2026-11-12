---
sherlock: DroidPhish
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, android, apk, phishing, mobile]
---

# DroidPhish — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Se entrega una imagen de disco de un dispositivo Android comprometido. Varios empleados recibieron un correo de phishing y se sospecha que instalaron una aplicación maliciosa. Hay que determinar cuándo arrancó el dispositivo, qué aplicación de correo se usó, cuándo llegó el mensaje, qué APK se descargó e instaló, qué permisos recibió y a qué C2 estaba configurada.

## Evidencias

- Imagen ext4 de Android (`android-x86`), montable o explorable con `debugfs`.
- `data/data/ch.protonmail.android/databases/db-mail`: base de datos de Proton Mail.
- `data/data/com.android.chrome/databases/History`: historial y descargas de Chrome.
- `data/system/packages.xml`: registro del gestor de paquetes.
- `data/misc/users/0/runtime-permissions.xml`: permisos concedidos.
- `data/misc/bootstat/last_boot_time_utc`: marca de arranque.

```bash
sha256sum DroidPhish.dd
file DroidPhish.dd
debugfs -R 'ls -l /data' DroidPhish.dd
```

## Investigación

### 1. Inventario y triaje

Se trabaja sobre una copia y con `TZ=UTC`. Android guarda muchas horas en milisegundos epoch y los mtimes dependen de la zona horaria de la shell.

```bash
TZ=UTC debugfs -R 'stat /data/misc/bootstat/last_boot_time_utc' DroidPhish.dd
```

Se extrae el directorio `data` para poder usar `sqlite3` y herramientas de APK:

```bash
debugfs -R 'rdump /data ./data' DroidPhish.dd
```

### 2. Línea temporal

- **Correo:** `db-mail` contiene el asunto y las cabeceras. La línea `Received:` de Proton es la hora de llegada; la columna `time` puede ser la fecha del remitente.
- **Descarga:** la tabla `downloads` de Chrome guarda la URL y la ruta de destino.
- **Instalación:** `packages.xml` contiene `it` (primer install time) en milisegundos epoch; se convierte a UTC.
- **Arranque:** el mtime de `last_boot_time_utc` da la referencia.

```bash
sqlite3 db-mail "select subject, datetime(time/1000,'unixepoch') from MessageEntity;"
sqlite3 History "select tab_url, target_path, datetime(start_time/1000,'unixepoch') from downloads;"
```

Se ordenan los eventos y se comprueba que la instalación ocurre minutos después de la llegada del correo y de la descarga.

### 3. Artefacto clave

El APK es el nexo. Se localiza el `base.apk` instalado, se calcula su SHA-256 y se compara con el fichero descargado:

```bash
sha256sum Download/Booking.apk
sha256sum data/app/<package>/base.apk
```

`packages.xml` relaciona el `codePath` con el paquete y su hora de instalación. `runtime-permissions.xml` lista los permisos concedidos; un número alto para una supuesta app de reservas es señal de abuso. En el dex, `strings` o Androguard permiten buscar cadenas base64 que decodifican a una IP y un puerto de C2.

```bash
python3 -c "from androguard.misc import AnalyzeAPK; a,d,dx=AnalyzeAPK('base.apk'); print(dx.get_strings())"
```

## Conclusiones

- El vector fue un correo de phishing en Proton Mail con un enlace a un APK alojado en un túnel de Cloudflare.
- Chrome descargó el APK y el usuario lo instaló como una falsa app de reservas.
- La app recibió permisos de runtime excesivos y contenía un C2 ofuscado en base64.
- Los IOCs son la URL de descarga, el hash del APK, el nombre del paquete y el C2.

## Lecciones

- Bloquear o alertar sobre la instalación de APK fuera de la tienda (sideloading).
- Filtrar enlaces a dominios de túnel desechables en el correo.
- Comparar permisos solicitados con la función declarada de la app.
- La analítica estática del dex encuentra C2 codificados sin ejecutar el malware.
