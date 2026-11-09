# Phishing infrastructure: from email to domain

**English** | [🇪🇸 Español](phishing-infrastructure.md)

A method to identify the infrastructure behind an impersonation email without touching the attacker's server.

## 1. From email to headers

```text
From:        <display name> <account@domain>
Return-Path: <bounce@another-domain>
Received:    from <host> (<IP>) by <mx>
Message-ID:  <id@domain>
Authentication-Results: spf=... dkim=... dmarc=...
```

- `From` is trivially forged; `Return-Path` and `Received` are not.
- Read `Received` **bottom-up**: the first is the attacker's server.
- `Authentication-Results` says what failed: SPF, DKIM or DMARC.
- A `Message-ID` whose domain differs from `From` exposes the panel used.

## 2. From domain to records

```bash
dig +short A <domain>
dig +short MX <domain>
dig +short TXT <domain>
dig +short NS <domain>
whois <domain> | grep -E "Creation|Registrar|Name Server"
```

Signs of purpose-built infrastructure:

- Its own MX (`mail.<domain>`) instead of a known provider.
- `TXT "v=spf1 a mx ip4:<IP> ~all"` with the server's own IP.
- `TXT "v=DMARC1; p=none;"` → monitoring without blocking.
- Domain registered days ago with `NS` at the same cheap provider.

## 3. Discover variants

```bash
dnstwist --registered <company>.com
dnstwist --geo <company>.com
```

Typical variants: different TLD, hyphen (`company-security`), doubled letter, homoglyphs (`rn` for `m`), deceptive subdomain (`company.com.login-x.tld`).

## 4. Certificates and reputation

- `crt.sh`: `https://crt.sh/?q=%25.<domain>` lists subdomains via Certificate Transparency, even before indexing.
- VirusTotal and URLScan: first seen, historical IPs, screenshots.
- Shodan/Censys on the IP: mail panel, ports 25/587/993 open, self-signed certificate.

## 5. Landing page

```bash
curl -sI https://<domain>/
curl -s https://<domain>/ | grep -E "form|action|password"
```

- Forms posting to another domain or to a Telegram bot.
- Exact clone of a legitimate login (compare the HTML hash).
- JavaScript obfuscation that builds the form at runtime.

## 6. Response

- Block domain and IP in the mail filter and DNS.
- Warn the users who received the message.
- Report to the registrar and hosting abuse contact with the headers.
- Rotate credentials of anyone who entered data.

## Typical errors

- Analysing HTML before headers: HTML is copied, headers are not.
- Confusing the `From` domain with the link's.
- Accepting an SPF `pass` when the attacker owns the domain.

MITRE: T1566.002, T1583.001, T1596.002.
