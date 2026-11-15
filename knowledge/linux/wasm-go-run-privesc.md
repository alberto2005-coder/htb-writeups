---
topic: Go — go run y Wasm como root
tags: [linux, go, wasm, go-run, privesc]
---

# Go — go run y Wasm como root

[🌐 English](wasm-go-run-privesc.en.md) | **Español**

## Concepto

`go run` compila y ejecuta un archivo desde el directorio actual. Si un usuario puede ejecutarlo como root y el programa lee `main.wasm` o un script relativo, puede reemplazar esos archivos para ejecutar código con privilegios de root.

## Cuándo aplica

- La regla sudo permite `go run` sobre un script.
- El programa lee archivos relativos (`main.wasm`, `deploy.sh`).
- El usuario puede escribir en el directorio o en uno anterior del `PATH`.

## Procedimiento

1. Leer el código Go y las rutas.
2. Crear un Wasm que devuelva el valor esperado.
3. Crear el script que se ejecuta después.
4. Ejecutar con sudo y obtener root.

## Comandos

```bash
# main.wasm devuelve 1 y deploy.sh lanza una reverse shell
sudo /usr/bin/go run /opt/wasm-functions/index.go
```

## Variantes

- Hijack de un módulo Go en el directorio.
- `go run` con un archivo escribible.
- Wasm que llama a una función importada.

## Limitaciones

- El directorio puede no ser escribible.
- El programa puede usar rutas absolutas.
- La versión de Go puede cachear el binario.

## Mitigación

- No permitir `go run` como root.
- Compilar binarios y usar rutas absolutas.
- Ejecutar servicios con un usuario dedicado.

## Detección

- `go run` en reglas sudo.
- Cambios en `main.wasm` o `deploy.sh`.
- Procesos Go con shells hijas.

## Referencias

- [0xdf — Ophiuchi](https://0xdf.gitlab.io/2021/07/03/htb-ophiuchi.html)
- [Go — go run](https://pkg.go.dev/cmd/go#hdr-Compile_and_run_Go_program)
- [WebAssembly — spec](https://webassembly.github.io/spec/)
