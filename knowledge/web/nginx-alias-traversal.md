---
topic: nginx alias traversal
tags: [web, nginx, path-traversal, misconfiguration]
---

# nginx alias traversal

[🇬🇧 English](nginx-alias-traversal.en.md) | **Español**

## Concepto

La directiva `alias` de nginx sustituye la parte de la URI que coincide con `location`. Si falta la barra final o no se normaliza la ruta, un `../` puede resolver fuera del directorio previsto y leer archivos arbitrarios.

## Cuándo aplica

- `location /static/ { alias /var/www/static/; }` con rutas controladas.
- Configuraciones que mezclan `alias` y `root`.
- Proxies que no normalizan `..`.

## Requisitos

1. Un `location` con `alias`.
2. Petición con `--path-as-is` para evitar normalización del cliente.
3. Ruta objetivo conocida.

## Procedimiento

```bash
curl --path-as-is 'http://<HOST>/assets/../../../../etc/passwd'
```

Si el `alias` no termina en `/`, se prueba la concatenación directa:

```bash
curl --path-as-is 'http://<HOST>/assets../flag.txt'
```

Se codifican los segmentos si hay un proxy:

```bash
curl --path-as-is 'http://<HOST>/assets/%2e%2e/%2e%2e/etc/passwd'
```

## Variantes

- **Alias sin slash final**: `alias /var/www/assets;`.
- **Location sin slash**: `location /assets { ... }`.
- **Doble codificación**: `%252e%252e`.
- **Proxy normalization**: probar con y sin `--path-as-is`.

## Limitaciones

- nginx moderno normaliza parte de la ruta.
- El proxy/WAF puede bloquear `..`.
- El archivo debe ser legible por el usuario de nginx.
- No todos los `alias` son vulnerables.

## Mitigación

- Usar `root` cuando sea posible.
- Añadir `/` final y normalizar.
- Rechazar `..` y validar la ruta resuelta.
- Revisar configuraciones con `nginx -T`.

## Detección

- Peticiones con `../` o `%2e%2e`.
- Accesos a `/etc/passwd` o archivos fuera del webroot.
- 200 en rutas que deberían ser 404.
- Fuzzing de directorios.

MITRE ATT&CK: T1190 (Exploit Public-Facing Application), T1083 (File and Directory Discovery).

## Referencias

- <https://nginx.org/en/docs/http/ngx_http_core_module.html#alias>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://book.hacktricks.xyz/pentesting-web/file-inclusion>
