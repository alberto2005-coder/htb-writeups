---
topic: Remote exploitation — socket reuse
tags: [pwn, buffer-overflow, shellcode, socket-reuse, windows]
---

# Remote exploitation — socket reuse

**English** | [🌐 Español](socket-reuse.md)

## Concept

In a network service, shellcode can reuse the already-open socket descriptor instead of creating a new connection. This enables an interactive second stage and avoids relying on an outbound reverse shell.

## When it applies

- The binary listens on the network and the overflow occurs in the client thread.
- EIP/RIP is controlled and there is room for shellcode.
- The socket remains open after the crash.

## Procedure

1. Find the offset with a pattern.
2. Identify a `JMP ESP` and the socket descriptor.
3. Build shellcode that calls `recv` and `exec` on the socket.
4. Send the second stage and get the shell.

## Commands

```bash
python3 exploit.py <IP> 9999
# the exploit reuses the socket and sends the second stage
nc <IP> 9999
```

## Variants

- `recv`+`CreateProcess` shellcode on Windows.
- `dup2` the socket to stdin/stdout on Linux.
- Intermediate stage with `msfvenom`.

## Limitations

- The socket may close on return.
- ASLR/NX require ROP or an executable region.
- Threaded services may vary the descriptor.

## Mitigation

- Build with ASLR, DEP and canaries.
- Validate lengths and use memory-safe languages.
- Segment the service and limit its privilege.

## Detection

- Service crashes followed by an interactive connection.
- Long patterns or shellcode bytes in traffic.
- Unexpected child processes of the service.

## References

- [0xdf — Hancliffe](https://0xdf.gitlab.io/2022/03/05/htb-hancliffe.html)
- [pwntools — shellcraft](https://docs.pwntools.com/en/stable/shellcraft.html)
- [HackTricks — stack overflow](https://book.hacktricks.wiki/en/binary-exploitation/stack-overflow/index.html)
