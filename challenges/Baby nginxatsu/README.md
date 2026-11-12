---
challenge: Baby nginxatsu
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nginx, alias-traversal, configuration]
---

# Baby nginxatsu — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una configuración de nginx con `alias` mal construida permite escapar del directorio previsto y leer archivos fuera del webroot. La flag está en una ruta accesible por traversal.

## Enunciado y superficie

- Web, Easy, retirado.
- Se entrega una URL servida por nginx.
- No hay credenciales iniciales.

```bash
curl -i http://<HOST>/
```

## Reconocimiento

Se revisan rutas y se identifican ubicaciones con `alias`. Se prueba traversal con y sin codificación:

```bash
curl --path-as-is 'http://<HOST>/assets/../../../../etc/passwd'
```

## Análisis

1. Se confirma la versión de nginx y la configuración expuesta.
2. Se identifica un `location /assets/ { alias /var/www/assets/; }`.
3. La falta de `/` final en `alias` permite concatenar `../`.
4. Se codifican los `../` si el proxy normaliza.
5. Se lee la ruta de la flag.

```bash
curl --path-as-is 'http://<HOST>/assets../flag.txt'
```

## Explicación del fallo

La directiva `alias` sin barra final y sin normalización permite que la ruta solicitada se resuelva fuera del directorio. Es un fallo de configuración, no de nginx en sí.

## Reproducción local

1. Configurar nginx con `alias` incorrecto.
2. Crear un archivo fuera del webroot.
3. Probar traversal.
4. Corregir el `alias` y comparar.
5. Redactar la flag.

## Evidencia

- Configuración/versión.
- Petición con traversal.
- Archivo leído y flag redactada.

## Lecciones aprendidas

- `alias` y `root` se comportan distinto.
- La barra final cambia la resolución.
- Los proxies pueden normalizar o no.
- La configuración es superficie de ataque.

## Mitigación y detección

- Usar `root` cuando sea posible.
- Añadir `/` final y normalizar rutas.
- Bloquear `..` y validar el path resuelto.
- Alertar de traversal en logs.

## Referencias

- <https://www.hackthebox.com/challenges/baby-nginxatsu>
- <https://nginx.org/en/docs/http/ngx_http_core_module.html#alias>
- <https://owasp.org/www-community/attacks/Path_Traversal>
