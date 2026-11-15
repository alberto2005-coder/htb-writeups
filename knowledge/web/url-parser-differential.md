---
topic: Diferencial de parseo de URL — proxy y backend
tags: [web, nginx, tomcat, proxy, auth-bypass]
---

# Diferencial de parseo de URL — proxy y backend

[🌐 English](url-parser-differential.en.md) | **Español**

## Concepto

Cuando Nginx y Tomcat interpretan la misma URL de forma distinta, una regla de autenticación del proxy puede aplicar a una ruta que el backend resuelve como otra. Secuencias como `..;/`, `%2e%2e` o barras normalizadas permiten alcanzar endpoints protegidos, como el manager de Tomcat, y desplegar una aplicación.

## Cuándo aplica

- Hay un proxy delante de un servidor de aplicaciones.
- La autenticación se aplica por ruta en el proxy.
- El backend normaliza la ruta de forma diferente.

## Procedimiento

1. Identificar el proxy y el backend por cabeceras y errores.
2. Probar variantes de traversal y normalización.
3. Comparar respuestas con y sin autenticación.
4. Usar la ruta que evita el control para desplegar o acceder.

## Comandos

```bash
curl -s -I http://<HOST>/
curl -s "http://<HOST>/manager/html"
curl -s "http://<HOST>/manager/..;/html"
curl -s "http://<HOST>/manager/%2e%2e;/html"
curl -u <USER>:<PASS> --upload-file shell.war "http://<HOST>/manager/text/deploy?path=/shell"
```

## Variantes

- Usar `;` para parámetros de matriz.
- Probar mayúsculas y codificación doble.
- Combinar con `X-Forwarded-*` si el backend confía en ellas.

## Limitaciones

- El proxy puede rechazar rutas no normalizadas.
- El backend puede estar parcheado.
- La autenticación puede estar también en el backend.

## Mitigación

- Normalizar y validar la ruta en ambos componentes.
- Aplicar autenticación en el backend, no solo en el proxy.
- Deshabilitar el manager y limitar despliegues.

## Detección

- Rutas con `..;/` o codificaciones inusuales.
- Respuestas 200 a rutas protegidas.
- Despliegues WAR no previstos.

## Referencias

- [0xdf — Seal](https://0xdf.gitlab.io/2021/11/13/htb-seal.html)
- [Tomcat — Security](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html)
- [CWE-436 — Interpretation Conflict](https://cwe.mitre.org/data/definitions/436.html)
