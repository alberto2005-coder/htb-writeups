---
topic: SSRF con oráculo HMAC
tags: [web, ssrf, hmac, proxy, internal-network]
---

# SSRF con oráculo HMAC

[🌐 English](hmac-oracle-ssrf.en.md) | **Español**

## Concepto

La aplicación firma peticiones internas con HMAC, pero expone un endpoint que firma parámetros arbitrarios. Combinado con un SSRF, el atacante construye peticiones válidas hacia servicios internos que de otro modo rechazarían la firma.

## Cuándo aplica

- SSRF con validación de URL pero sin restricción de destino real.
- Endpoint de firma que acepta datos del usuario.
- Servicios internos que confían en una cabecera HMAC.

## Procedimiento

1. Identificar el parámetro firmado y el formato del HMAC.
2. Usar el oráculo para firmar una petición propia.
3. Enviar la petición a través del SSRF.
4. Repetir para enumerar rutas y acciones internas.

```bash
curl 'http://<HOST>/sign?data=GET%20/internal%20HTTP/1.1'
curl 'http://<HOST>/proxy?url=http://internal/&sig=<HMAC>'
# Proxy local que firma y reenvía
python3 ssrf_hmac_proxy.py --target http://<HOST> --listen 8000
```

## Variantes

- Firma de cuerpo, ruta o método por separado.
- HMAC con clave derivada de un usuario.
- SSRF ciego con callback y timing.
- Redirecciones que cambian el destino después de firmar.

## Limitaciones

- El oráculo debe firmar exactamente el formato esperado.
- El SSRF debe permitir el destino interno.
- La clave puede incluir contexto no controlable.

## Mitigación y detección

- No exponer un oráculo de firma; firmar solo operaciones predefinidas.
- Validar destinos, resolver DNS y bloquear rangos internos.
- Usar mTLS y autorización por servicio, no solo HMAC.

## Referencias

- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://portswigger.net/web-security/ssrf>
- <https://attack.mitre.org/techniques/T1190/>
