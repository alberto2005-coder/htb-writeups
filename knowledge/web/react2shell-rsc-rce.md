---
topic: React2Shell — deserialización RSC (CVE-2025-55182)
tags: [web, react, nextjs, rsc, cve-2025-55182, deserialization, rce]
---

# React2Shell — deserialización RSC (CVE-2025-55182)

[🌐 English](react2shell-rsc-rce.en.md) | **Español**

## Concepto

React Server Components deserializa datos enviados por el cliente para las Server Actions. En versiones vulnerables, un payload multipart manipula la cadena de prototipos y alcanza `child_process`, lo que permite ejecución remota sin autenticación.

## Cuándo aplica

- La app usa NextJS/React con RSC y Server Actions.
- La versión está afectada por CVE-2025-55182.
- Se puede enviar un POST multipart con `Next-Action`.

## Procedimiento

1. Extraer las versiones de los chunks JS y cabeceras.
2. Identificar una Server Action válida.
3. Construir el cuerpo multipart con la cadena de prototipos.
4. Enviar con `curl` y comprobar la ejecución.

## Comandos

```bash
curl -s http://<IP>:3000 | grep -oE '/_next/static/[^"\\]+\.js'
curl -X POST http://<IP>:3000/ -H 'Next-Action: <ACTION>' \
  -H 'Content-Type: multipart/form-data; boundary=----R2S' \
  --data-binary @r2s-body.txt
```

## Variantes

- Server Actions con distintos IDs.
- Deserialización de props en `flight` datos.
- Encadenar con el inspector de Node.

## Limitaciones

- Versiones parcheadas rechazan el payload.
- La app puede no usar Server Actions.
- WAF puede bloquear el multipart.

## Mitigación

- Actualizar React/NextJS a versiones corregidas.
- Validar el formato de las Server Actions.
- No confiar en datos del cliente para deserializar.

## Detección

- POST con `Next-Action` y cuerpos multipart anómalos.
- Procesos hijos de Node desde el servidor web.
- Versiones vulnerables en producción.

## Referencias

- [0xdf — Reactor](https://0xdf.gitlab.io/2026/10/03/htb-reactor.html)
- [NVD — CVE-2025-55182](https://nvd.nist.gov/vuln/detail/CVE-2025-55182)
- [React — security advisory](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)
