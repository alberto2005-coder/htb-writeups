---
topic: gRPC and Protobuf — enumeration and SSRF
tags: [network, grpc, protobuf, ssrf, enumeration]
---

# gRPC and Protobuf — enumeration and SSRF

**English** | [🌐 Español](grpc-protobuf-enumeration.md)

## Concept

gRPC uses Protocol Buffers to define services and messages over HTTP/2. If the `.proto` file or service documentation is obtained, a client can be generated and internal methods called. A method that accepts a URL can become an SSRF into loopback services.

## When it applies

- A port speaks HTTP/2 and is not a conventional web server.
- Documentation, a leaked `.proto` or gRPC reflection is available.
- The service accepts URLs, paths or destinations processed server-side.

## Procedure

1. Identify the service and test reflection with `grpcurl list`.
2. Rebuild the `.proto` from documentation or the binary.
3. Generate stubs with `grpc_tools.protoc` and call the method.
4. Replace the URL with `127.0.0.1:<PORT>` and observe the response.

## Commands

```bash
grpcurl -plaintext <IP>:9000 list
python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. feed.proto
grpcurl -plaintext -proto feed.proto -d '{"data":"<BASE64>"}' <IP>:9000 Print/Feed
curl -s http://127.0.0.1:8983/solr/
```

## Variants

- Use `gopher://` to send a complete HTTP request to an internal service.
- Iterate the URL field across ports and paths to enumerate loopback.
- Generate a Python client when `grpcurl` is unavailable.

## Limitations

- Without a `.proto` or reflection, messages must be reconstructed.
- The service may validate the schema or destination host.
- HTTP/2 and TLS may require `-insecure` or a proxy.

## Mitigation

- Disable reflection in production and require authentication.
- Validate destinations against an allowlist and block egress to loopback.
- Segment internal services from the component that fetches.

## Detection

- gRPC calls to methods the application does not normally use.
- Connections from the service to `127.0.0.1` or internal ranges.
- Use of `grpcurl` or generated clients from unusual hosts.

## References

- [0xdf — Laser](https://0xdf.gitlab.io/2020/12/19/htb-laser.html)
- [gRPC — Introduction](https://grpc.io/docs/what-is-grpc/introduction/)
- [Protocol Buffers — Language guide](https://protobuf.dev/programming-guides/proto3/)
