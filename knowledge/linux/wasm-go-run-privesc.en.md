---
topic: Go — go run and Wasm as root
tags: [linux, go, wasm, go-run, privesc]
---

# Go — go run and Wasm as root

**English** | [🌐 Español](wasm-go-run-privesc.md)

## Concept

`go run` compiles and runs a file from the current directory. If a user can run it as root and the program reads `main.wasm` or a relative script, those files can be replaced to run code as root.

## When it applies

- The sudo rule allows `go run` on a script.
- The program reads relative files (`main.wasm`, `deploy.sh`).
- The user can write to the directory or an earlier `PATH` entry.

## Procedure

1. Read the Go code and paths.
2. Create a Wasm returning the expected value.
3. Create the script executed afterwards.
4. Run with sudo and get root.

## Commands

```bash
# main.wasm returns 1 and deploy.sh launches a reverse shell
sudo /usr/bin/go run /opt/wasm-functions/index.go
```

## Variants

- Hijack a Go module in the directory.
- `go run` with a writable file.
- Wasm calling an imported function.

## Limitations

- The directory may not be writable.
- The program may use absolute paths.
- The Go version may cache the binary.

## Mitigation

- Do not allow `go run` as root.
- Compile binaries and use absolute paths.
- Run services as a dedicated user.

## Detection

- `go run` in sudo rules.
- Changes to `main.wasm` or `deploy.sh`.
- Go processes with child shells.

## References

- [0xdf — Ophiuchi](https://0xdf.gitlab.io/2021/07/03/htb-ophiuchi.html)
- [Go — go run](https://pkg.go.dev/cmd/go#hdr-Compile_and_run_Go_program)
- [WebAssembly — spec](https://webassembly.github.io/spec/)
