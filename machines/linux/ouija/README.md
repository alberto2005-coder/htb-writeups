---
machine: Ouija
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, haproxy, request-smuggling, hash-extension, php-extension, integer-overflow]
---

# Ouija — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un request smuggling en HAProxy permite alcanzar un sitio de desarrollo interno. Los detalles de la API permiten un ataque de hash length extension para forjar una clave de administrador y leer una clave SSH. Root explota un desbordamiento de enteros en un módulo PHP propio hasta lograr escritura arbitraria.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
# Request smuggling CL.TE
curl --path-as-is -H "Content-Length: 6" -H "Transfer-Encoding: chunked" http://ouija.htb/
# Hash length extension
hashpump -s <SIG> -d "user=guest" -a "&admin=1" -k <LEN>
# API
curl -H "X-API-Key: <FORGED>" http://ouija.htb/api/admin
# Módulo PHP
php -i | grep extension_dir
gdb -q -p <PID>
python3 exploit.py
```

## Enumeración

- HAProxy delante de frontend y backend con parsing inconsistente.
- Sitio de desarrollo y API con firma tipo `hash(secret || data)`.
- Módulo PHP nativo con un entero sin comprobar.

## Acceso inicial

Se envía una petición con `Content-Length` y `Transfer-Encoding` contradictorios para que HAProxy y el backend discrepen y el backend procese una ruta interna. El sitio de desarrollo filtra la API y su formato de firma; con `hashpump` se extiende el mensaje y se forja la clave de administrador.

## Escalada de privilegios

La API de administración permite leer una clave SSH y entrar al host. Se localiza un módulo PHP compilado que calcula un índice con un entero; se envía un valor que desborda y sobrescribe variables de pila, lo que se aprovecha para obtener escritura arbitraria y ejecutar como root.

## Evidencia

- Petición smuggled aceptada por el backend.
- Clave de administrador forjada y clave SSH leída.
- Desbordamiento del módulo y shell de root.

## Lecciones aprendidas

- Proxy y backend deben normalizar igual las peticiones.
- `hash(secret || data)` es vulnerable a length extension.
- Los módulos nativos necesitan validación de enteros y límites.

## Mitigación y detección

- Rechazar peticiones con cabeceras ambiguas y normalizar en ambos extremos.
- Usar HMAC en lugar de concatenación de secreto.
- Compilar con `-fstack-protector` y revisar módulos nativos.

## Referencias

- [0xdf — Ouija](https://0xdf.gitlab.io/2024/05/18/htb-ouija.html)
- [HAProxy — Configuration](https://docs.haproxy.org/)
- [Hack The Box — Ouija](https://app.hackthebox.com/machines/ouija)
