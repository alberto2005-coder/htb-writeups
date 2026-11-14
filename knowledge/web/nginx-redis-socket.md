---
topic: Redis por socket Unix en Nginx
tags: [web, nginx, redis, unix-socket, proxy-pass]
---

# Redis por socket Unix en Nginx

[🌐 English](nginx-redis-socket.en.md) | **Español**

## Concepto

Una regla `proxy_pass` que apunta a un socket Unix de Redis permite que una petición HTTP se traduzca en comandos RESP. Si el socket no exige autenticación, el atacante puede leer o escribir claves, sessions y configuraciones.

## Cuándo aplica

- Nginx reenvía un prefijo a `unix:/var/run/redis/redis.sock`.
- Redis escucha solo en el socket, pero Nginx lo expone.
- La aplicación usa Redis para sesiones, roles o caché.

## Procedimiento

1. Revisar la configuración de Nginx y los sockets accesibles.
2. Identificar un endpoint que llegue al `proxy_pass`.
3. Enviar comandos RESP en el cuerpo o en la ruta, según la regla.
4. Leer claves de sesión o modificar un rol.
5. Escribir un archivo si Redis tiene un directorio escribible.

```bash
curl -s "http://<HOST>/redis/" --data-binary $'PING\r\n'
```

## Variantes

- `proxy_pass` con una URI que conserva el prefijo.
- Redis con `requirepass` débil o reutilizada.
- Escritura de un webshell mediante `CONFIG SET dir` y `SAVE`.

## Limitaciones

- Nginx puede normalizar o bloquear el método.
- Redis puede estar en modo protegido.
- El socket puede tener permisos restrictivos.

## Mitigación

- No exponer Redis a través de Nginx.
- Requerir autenticación y `protected-mode`.
- Ejecutar Redis con un usuario sin escritura en el webroot.

## Detección

- Peticiones HTTP con `PING`, `GET`, `SET` o `CONFIG`.
- Accesos al socket desde Nginx.
- Nuevos archivos en el directorio de trabajo de Redis.

## Referencias

- <https://redis.io/docs/latest/operate/oss_and_stack/management/security/>
- <https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass>
- <https://attack.mitre.org/techniques/T1190/>
