---
machine: WhiteRabbit
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, uptime-kuma, wikijs, n8n, sqli, restic, container, password-generator, privesc]
---

# WhiteRabbit — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Uptime Kuma allows a login bypass and a shell in its container as `bob`. WikiJS documents an n8n flow with HMAC signing and SQLi; a proxy that signs requests dumps the database and reveals restic commands. A backup holds SSH keys and `restic --password-command` gives root in the container and access to `morpheus` on the host. A timestamp-seeded password generator allows calculating `neo`'s password, and `neo` can run any command as root.

## Recon

```bash
nmap -Pn -sCV -p22,80,2222 <IP>
```

- `22` host SSH, `2222` container SSH and `80` Caddy.
- `ffuf` finds `whiterabbit.htb`, `uptime.whiterabbit.htb` and a WikiJS on a random subdomain.
- The main site mentions Uptime Kuma, n8n, GoPhish and Stalwart.

## Enumeration

- Uptime Kuma uses Socket.IO and has a login bypass.
- Create a monitor/status page and enumerate internal hosts.
- WikiJS documents the `GoPhish -> n8n` flow, the `x-gophish-signature` signature and the SQL query.
- The flow export reveals the HMAC secret and the SQLi in the email.

## Foothold

Run a `mitmproxy` proxy that recomputes each request signature, and let `sqlmap` dump the database through it. The database holds restic commands, the `.restic_passwd` password and the `neo-password-generator` run.

```bash
mitmproxy -s signature_proxy.py -p 8888 --mode regular
sqlmap -r request.req --proxy http://127.0.0.1:8888
```

## Lateral movement

The restic repo holds `bob.7z` with SSH keys; crack it with `7z2john` and `john`. In the container, `bob` can run `restic` as root; `--password-command` runs commands and allows copying `/bin/bash` and making it SUID. The `morpheus` key in `/root` enters the host.

```bash
sudo restic check --password-command 'cp /bin/bash /tmp/rootbash'
sudo restic check --password-command 'chmod 6777 /tmp/rootbash'
ssh -i morpheus morpheus@whiterabbit.htb
```

## Privilege escalation

`morpheus` finds `neo-password-generator`, which seeds `srand()` with the millisecond timestamp. Database logs reveal when it ran; generate every password for that second and `hydra` finds `neo`'s. `neo` can run any command as root.

```bash
python3 gen_passwords.py '2024-08-30 14:40:42'
hydra -l neo -P neo_passwords ssh://whiterabbit.htb
sudo -i
```

## Evidence

- Uptime Kuma and shell as `bob`.
- WikiJS, HMAC signature and n8n SQLi.
- Database with restic commands.
- `restic --password-command` and SSH keys.
- Timestamp password generator and `neo`.

## Lessons learned

- A monitoring panel can leak the internal topology.
- Signing requests does not stop SQLi if the secret leaks.
- `restic --password-command` is execution when the argument is controlled.
- A PRNG seeded with time is predictable.

## Mitigation and detection

- Update Uptime Kuma and require MFA.
- Parameterize queries and protect the HMAC secret.
- Do not allow `--password-command` for untrusted users.
- Use a CSPRNG and never derive passwords from the clock.

## References

- [0xdf — WhiteRabbit](https://0xdf.gitlab.io/2025/12/13/htb-whiterabbit.html)
- [IppSec — WhiteRabbit](https://www.youtube.com/watch?v=IVwZAINSCwo)
- [Hack The Box — WhiteRabbit](https://app.hackthebox.com/machines/whiterabbit)
