---
topic: Nginx off-by-slash
tags: [web, nginx, alias, proxy-pass, traversal]
---

# Nginx off-by-slash

[🌐 English](nginx-off-by-slash.en.md) | **Español**

## Concepto

Una regla `location /admin` con `alias` o `proxy_pass` sin barra final puede interpretar `/admin../ruta` como un salto al directorio padre. Esto permite alcanzar aplicaciones o archivos fuera del prefijo previsto.

## Cuándo aplica

- Nginx usa `alias` o `proxy_pass` sin barra final.
- Existe una ruta protegida o no enlazada.
- El backend confía en la ruta reescrita.

## Procedimiento

1. Probar `/admin..` y `/admin../`.
2. Buscar un `index.php` o una ruta conocida.
3. Ajustar el número de segmentos.
4. Acceder al panel o archivo interno.

```bash
curl -i 'http://<IP>/admin../admin_staging/index.php'
curl -i 'http://<IP>/admin../admin_staging/'
```

## Variantes

- Aplicar el mismo truco a `alias` de archivos estáticos.
- Combinar con un LFI para leer configuración.
- Usar codificaciones de barra.

## Limitaciones

- La regla debe estar mal formada.
- El backend debe aceptar la ruta resultante.
- Nginx puede normalizar la URI.

## Mitigación y detección

- Añadir barras finales y usar `location =` o `^~`.
- Normalizar la URI antes de reescribir.
- Auditar configuraciones de proxy y alias.

## Referencias

- <https://nginx.org/en/docs/http/ngx_http_core_module.html#alias>
- <https://i.blackhat.com/us-18/Wed-August-8/us-18-Orange-Tsai-Breaking-Parser-Logic-Take-Your-Path-Normalization-Off-And-Pop-0days-Out-2.pdf>
- <https://attack.mitre.org/techniques/T1190/>
