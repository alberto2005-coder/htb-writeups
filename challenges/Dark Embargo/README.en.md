---
challenge: Dark Embargo
category: Challenge
type: web
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
solved: 2026-11-08
tags: [web, php, memory-corruption, aslr, cve]
---

# Dark Embargo — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> The challenge has no user or root flag: the only proof is reading `/flag.txt`.
> Achievement: https://labs.hackthebox.com/achievement/challenge/4187928/1926

## TL;DR

A `php:8.4.26-apache` container with a static landing page. The only clue is `X-Powered-By: PHP/8.4.26`, the last release carrying the `session.upload_progress` bug (CVE-2026-109618 / CVE-2026-109619). A multipart body that crosses `memory_limit` triggers an out-of-memory bailout that skips teardown and leaves the session pointers dangling. One of them leaks memory through `Set-Cookie` and defeats ASLR; the other is used to forge a `zend_array` whose `pDestructor` is `zif_system`. Result: unauthenticated RCE as `www-data` and `/flag.txt` for the taking.

## Surface

- Web challenge, Medium. The whole build ships as a zip: `Dockerfile`, `index.php`, `flag.txt` and `build_docker.sh`.
- The `Dockerfile` is a stock image with no custom `php.ini`: `FROM php:8.4.26-apache`, copies `index.php`, drops `flag.txt` at `/flag.txt` with `chmod 0777`.
- `index.php` contains zero `<?php` tags: it is a decoy. No forms, no parameters, no dynamic endpoints.

That leaves the attack where nobody looks: the PHP version and its defaults.

## Recon

```bash
curl -s -I http://<IP>:<PORT>/
```

```text
HTTP/1.1 200 OK
Server: Apache/2.4.69 (Debian)
X-Powered-By: PHP/8.4.26
Content-Type: text/html; charset=UTF-8
```

Check the defaults that matter, inside the container:

```bash
docker exec dark_embargo php -i | grep -Ei 'memory_limit|upload_progress.enabled|session.save_path|post_max_size'
```

```text
memory_limit => 128M => 128M
session.save_path => no value => no value
session.upload_progress.enabled => On => On
post_max_size => 8M => 8M
```

Four defaults carry the whole exploit:

- `memory_limit = 128M` is the threshold to cross.
- `session.upload_progress.enabled = On` opens the pre-script code path.
- An empty `session.save_path` falls back to `/tmp`, which is writable.
- `display_errors = Off` means none of this reaches the response: the only output channel is a header.

## How `session.upload_progress` works

The feature exists for progress bars: send a `PHP_SESSION_UPLOAD_PROGRESS` field in a multipart body and PHP records how many bytes have arrived. What matters is **where** it runs: inside the multipart parser (`main/rfc1867.c`), before any script executes. That is why it works on a page with no PHP in it.

You can watch it happen with a slow upload, because `session.upload_progress.cleanup` deletes the record as soon as the upload finishes:

```bash
head -c 5M /dev/zero > /tmp/big
curl -s -b 'PHPSESSID=demo' -F 'PHP_SESSION_UPLOAD_PROGRESS=x' \
     -F 'file=@/tmp/big' --limit-rate 80k http://<IP>:<PORT>/index.php &
sleep 2
docker exec dark_embargo cat /tmp/sess_demo
```

```text
upload_progress_x|a:5:{s:10:"start_time";i:...;s:14:"content_length";i:5243210;
s:15:"bytes_processed";i:164085;s:4:"done";b:0;...}
```

`done";b:0` proves the request was caught mid-flight. It is a pre-auth path that allocates and frees heap objects from data we control: raw material for a use-after-free.

## The bug: an OOM bailout with no cleanup

`memory_limit` is not a `malloc` returning `NULL`. When ZendMM cannot satisfy an allocation it calls `zend_mm_safe_error`, which ends in `zend_bailout`: a `longjmp` back to the top of the request handler.

That jump swallows the teardown. The session module never clears its globals and ZendMM only resets its bookkeeping, so the two pointers it held — the session id and `$_SESSION` — are left pointing at memory that is now free. Apache prefork children are long-lived, so the broken state persists in that worker.

In the source those two fields live in `ps_globals`: `id` at `+0x10` and `http_session_vars` at `+0x168`. GDB shows that after the abort both point into the same 2 MB chunk:

```text
id.value                 = 0x7f0c810640c0   → chunk + 0x640c0
http_session_vars.value  = 0x7f0c8107a720   → chunk + 0x7a720
```

Two offsets stable for this build. Everything after that is coaxing the allocator into handing the chunk back, one size class at a time, so our forged bytes land where those stale pointers read.

## Debug environment and offsets

None of this is visible from outside, so a second copy of the same image is started with GDB inside. Two things are needed: `CAP_SYS_PTRACE` (Docker drops it by default) and a single worker for a predictable process.

```bash
cat > mpm1.conf <<'EOF'
StartServers 1
MinSpareServers 1
MaxSpareServers 1
MaxRequestWorkers 1
ServerLimit 1
MaxConnectionsPerChild 0
EOF

docker run -d --name dark_dbg -p 127.0.0.1:8088:80 \
  --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
  -v "$PWD/mpm1.conf:/etc/apache2/mods-available/mpm_prefork.conf" dark_embargo

docker exec -it dark_dbg bash
apt-get update -qq && apt-get install -y gdb
```

`libphp.so` has no debug info but keeps its symbol table:

```bash
gdb -q -batch -iex 'set auto-load safe-path /' \
  -ex 'info address zif_system' \
  -ex 'info address zval_ptr_dtor' \
  -ex 'info address ps_globals' \
  /usr/lib/apache2/modules/libphp.so
```

```text
zif_system     at 0x465370
zval_ptr_dtor  at 0x65eb60
ps_globals     at 0x1316820
```

Those are offsets from `libphp.so`'s load base, which pins the three build constants:

| Name | Value | Source |
|---|---|---|
| `ZIF_SYSTEM` | `libphp + 0x465370` | `info address` |
| `ZVAL_PTR_DTOR` | `libphp + 0x65EB60` | `info address`, leak landmark |
| `S_OFFSET` | `chunk + 0xF5398` | `popen` sweep, see below |

## Leaking ASLR through the session cookie

With no output on the page, the trick is to make PHP write its own memory into a header. At the end of a request PHP may send `Set-Cookie: PHPSESSID=<id>`, and the id is a `zend_string` percent-encoded by `php_url_encode()`. If the dangling id is reclaimed with a fake header whose `len` field claims ~600 KB, `php_url_encode` reads 600 KB of neighbouring heap straight into the cookie.

The decoder's two rules:

- The most frequent 2 MB-aligned value is the chunk base: many pointers inside a chunk point back to it, and `addr & ~0x1fffff` rounds it cleanly.
- Any value whose low 12 bits match `zval_ptr_dtor`'s page offset is a pointer to that function; the base is `value - 0x65EB60`.

```python
def decode_bases(raw):
    heaps = Counter()
    for i in range(len(raw) - 7):
        v = int.from_bytes(raw[i:i+8], "little")
        if PTR_LO <= v < PTR_HI:            # 2^44 .. 2^47
            heaps[v & ~0x1FFFFF] += 1
    heap, hits = heaps.most_common(1)[0]
    ...
    if (v & 0xFFF) == (ZVAL_PTR_DTOR & 0xFFF):
        mods[v - ZVAL_PTR_DTOR] += 1
```

At least eight consistent hits are required before trusting a base. The pointer window is kept wide (`0x1000_0000_0000` to `0x8000_0000_0000`) because ASLR can place the chunk anywhere in the user range; assuming a fixed high prefix is the usual reason a leak is flaky.

Before that the worker has to be recycled: a ~129 MB chunked upload kills it with OOM so its replacement starts on a predictable chunk, then a clean session is planted with a known id.

## From dangling pointer to `system()`

With the bases known, the freed `$_SESSION` (`chunk + 0x7a720`) is reclaimed by a spray that points at a fake `zend_array`. Every spray value carries a fake `zend_reference` every 32 bytes, aimed at a 384-byte array that also lives in the spray. That fake array has:

- `pDestructor` at `+0x30` = `zif_system`;
- a fake bucket at `+0x20` holding a string `zval`;
- a fake `zend_string` at `+0x80` whose bytes, at `+0x98`, are the command.

The preceding `arm` is what crosses the limit: about 880 fields with nested names like `files[R00000][a][a]…` (64 levels) and `filename=""`. No temp file is created, but every intermediate `HashTable` is still allocated, so the heap passes 128 MB while the body on the wire is a few hundred KB.

The destruction chain is the whole exploit, bottom-up:

```text
popen("id>/tmp/p1")
  ← php_exec ← php_exec_ex
    ← zend_hash_destroy (pDestructor = zif_system)
      ← zend_array_destroy
        ← zend_reference_destroy   (our zend_reference over $_SESSION)
```

`S_OFFSET` is the only value that depends on spray geometry. It is recovered by breaking on `popen` and sweeping the argument until it trips:

```bash
W=$(pgrep -P $(pgrep -f '[a]pache2 -DFOREGROUND' | head -1) | head -1)
gdb -q -p "$W" -iex 'set auto-load safe-path /'
(gdb) break popen
(gdb) x/s $rdi        # 0x7f0c810f5430: "id>/tmp/p1"
(gdb) printf "S_OFFSET = %#lx\n", ($rdi - 0x98) & 0x1fffff
```

```text
S_OFFSET = 0xf5398
```

## Against the real target: 149 workers pinned

The challenge uses the stock prefork pool, `MaxRequestWorkers 150`. Producer, consumer, `arm` and `fire` must land on the **same** child with the same heap, so 149 children are tied up with chunked uploads that never finish (a 256-byte chunk every 0.3 s), leaving one child free for the whole sequence. The script does this with threads and a shared `Event` that releases them at the end.

```bash
python3 exploit.py --url http://<IP>:<PORT>/ \
  --cmd 'cat /flag.txt>/var/www/html/fx' --fetch /fx
```

```text
[*] saturating the worker pool (149 blockers)
[*] leaking bases
[+] chunk=0x7f97b8e00000 libphp=0x7f97baacf000
[*] arm+fire 1/8 sent
PROOF: HTB{...}
```

The bailout is non-corrupting: the child survives and the `fire` lands within an attempt or two. The command slot is 200 bytes, so a one-line reverse shell fits without staging; this box has no outbound access, so the practical route is to write the flag into the web root and read it over HTTP.

Script knobs: `--blockers 149`, `--rounds 8`, `--leak-tries 6`, `--no-saturate` for the single-worker container, `--proof-file`/`--container` to read the proof from inside Docker, `--no-verify` for self-signed certificates.

## Evidence

- `id` → `uid=33(www-data) gid=33(www-data)`.
- `cat /flag.txt` → `HTB{...}` (redacted).
- A ~600 KB `Set-Cookie` full of readable pointers during the leak.

## Lessons learned

- **The script did not compile.** The header docstring had no closing `"""`, so Python swallowed the file up to the docstring in `rotate()` and died with `SyntaxError: invalid decimal literal` on line 168. The docstring is now closed and lists the three build constants, which is where they get re-tuned. `python -m py_compile` and `--help` both pass.
- Losing half an hour on the leak by assuming a fixed high prefix. The chunk can land anywhere in the `0x7f...` range: mask and count, do not guess.
- Lying `len` fields cut both ways: in the leak the bogus length *is* the bug, so it pays to know whether a function walks bytes or trusts a terminator.
- An OOM is not a crash, it is a `longjmp`. That explains why the worker survives and why the dirty state persists across requests.
- The `libphp.so` offsets belong to the exact build. A different image means repeating `info address` and the `popen` sweep; everything else (the 2 MB mask, the spray geometry) stays.

## Mitigations and detection

- Upgrade to a PHP release with the handler fixed (8.4.27 or later in the 8.4 branch).
- If progress bars are unused, `session.upload_progress.enabled = Off`; it is a one-line mitigation that breaks nothing in most applications.
- A realistic per-pool `memory_limit` and a `MaxRequestWorkers` sized to the container: the attack depends on pinning 149 children.
- Detection rules: multipart bodies with hundreds of nested `files[...][...]` fields and `filename=""`, chunked uploads over 100 MB, `PHPSESSID` cookies hundreds of KB long, and abnormally large `Set-Cookie` responses.
- In Apache logs, bursts of children in `W` state from a single client with no `Content-Length`.
- MITRE: T1190, T1059.004, T1027.

## References

- CVE-2026-109618 and CVE-2026-109619 (PHP 8.4, `session.upload_progress`).
- PHP source: `main/rfc1867.c`, `ext/session/php_session.h`, `Zend/zend_alloc.c`.
- MITRE ATT&CK: T1190, T1059.004.
