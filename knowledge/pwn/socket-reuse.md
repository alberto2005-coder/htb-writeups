---
topic: Explotación remota — reutilización del socket
tags: [pwn, buffer-overflow, shellcode, socket-reuse, windows]
---

# Explotación remota — reutilización del socket

[🌐 English](socket-reuse.en.md) | **Español**

## Concepto

En un servicio de red, el shellcode puede reutilizar el descriptor del socket ya abierto en lugar de crear una conexión nueva. Esto permite una segunda etapa interactiva y evita depender de una reverse shell saliente.

## Cuándo aplica

- El binario escucha en red y el overflow ocurre en el hilo del cliente.
- Se controla EIP/RIP y hay espacio para shellcode.
- El socket sigue abierto tras el crash.

## Procedimiento

1. Calcular el offset con un patrón.
2. Identificar un `JMP ESP` y el descriptor del socket.
3. Construir shellcode que llame a `recv` y `exec` sobre el socket.
4. Enviar la segunda etapa y obtener la shell.

## Comandos

```bash
python3 exploit.py <IP> 9999
# el exploit reutiliza el socket y envía la segunda etapa
nc <IP> 9999
```

## Variantes

- Shellcode `recv`+`CreateProcess` en Windows.
- `dup2` del socket a stdin/stdout en Linux.
- Etapa intermedia con `msfvenom`.

## Limitaciones

- El socket puede cerrarse al retornar.
- ASLR/NX requieren ROP o una región ejecutable.
- El servicio puede usar threads y el descriptor variar.

## Mitigación

- Compilar con ASLR, DEP y canarios.
- Validar longitudes y usar lenguajes seguros.
- Segmentar el servicio y limitar su privilegio.

## Detección

- Crashes del servicio seguidos de una conexión interactiva.
- Patrones largos o bytes de shellcode en el tráfico.
- Procesos hijos inesperados del servicio.

## Referencias

- [0xdf — Hancliffe](https://0xdf.gitlab.io/2022/03/05/htb-hancliffe.html)
- [pwntools — shellcraft](https://docs.pwntools.com/en/stable/shellcraft.html)
- [HackTricks — stack overflow](https://book.hacktricks.wiki/en/binary-exploitation/stack-overflow/index.html)
