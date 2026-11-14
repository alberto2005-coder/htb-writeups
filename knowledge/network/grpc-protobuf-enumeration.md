---
topic: gRPC y Protobuf — enumeración y SSRF
tags: [network, grpc, protobuf, ssrf, enumeration]
---

# gRPC y Protobuf — enumeración y SSRF

[🌐 English](grpc-protobuf-enumeration.en.md) | **Español**

## Concepto

gRPC usa Protocol Buffers para definir servicios y mensajes sobre HTTP/2. Si se obtiene el archivo `.proto` o la documentación del servicio, se puede generar un cliente y llamar métodos internos. Un método que recibe una URL puede convertirse en un SSRF hacia servicios de loopback.

## Cuándo aplica

- Un puerto responde con HTTP/2 y no es un servidor web convencional.
- Hay documentación, un `.proto` filtrado o reflexión gRPC habilitada.
- El servicio acepta URLs, rutas o destinos que procesa desde el servidor.

## Procedimiento

1. Identificar el servicio y probar reflexión con `grpcurl list`.
2. Reconstruir el `.proto` a partir de la documentación o del binario.
3. Generar stubs con `grpc_tools.protoc` y llamar al método.
4. Sustituir la URL por `127.0.0.1:<PUERTO>` y observar la respuesta.

## Comandos

```bash
grpcurl -plaintext <IP>:9000 list
python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. feed.proto
grpcurl -plaintext -proto feed.proto -d '{"data":"<BASE64>"}' <IP>:9000 Print/Feed
curl -s http://127.0.0.1:8983/solr/
```

## Variantes

- Usar `gopher://` para enviar una petición HTTP completa a un servicio interno.
- Iterar el campo de URL sobre puertos y rutas para enumerar loopback.
- Generar un cliente en Python cuando `grpcurl` no esté disponible.

## Limitaciones

- Sin `.proto` ni reflexión, hay que reconstruir los mensajes.
- El servicio puede validar el esquema o el host destino.
- HTTP/2 y TLS pueden requerir `-insecure` o un proxy.

## Mitigación

- Deshabilitar reflexión en producción y exigir autenticación.
- Validar destinos contra una allowlist y bloquear egress a loopback.
- Segmentar los servicios internos del componente que hace fetch.

## Detección

- Llamadas gRPC a métodos que no usa la aplicación normal.
- Conexiones desde el servicio a `127.0.0.1` o rangos internos.
- Uso de `grpcurl` o clientes generados desde hosts no habituales.

## Referencias

- [0xdf — Laser](https://0xdf.gitlab.io/2020/12/19/htb-laser.html)
- [gRPC — Introduction](https://grpc.io/docs/what-is-grpc/introduction/)
- [Protocol Buffers — Language guide](https://protobuf.dev/programming-guides/proto3/)
