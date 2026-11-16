---
topic: qpdf — lectura de archivos privilegiados con adjuntos
tags: [linux, qpdf, pdf, sudo, file-read, privesc]
---

# qpdf — lectura de archivos privilegiados con adjuntos

[🌐 English](qpdf-attachment-file-read.en.md) | **Español**

## Concepto

`qpdf` puede crear un PDF vacío y adjuntarle archivos con `--add-attachment`. Si el binario se ejecuta con sudo, el archivo se lee con los privilegios de root y queda dentro del PDF. El atacante solo necesita poder extraer el adjunto después. No es una vulnerabilidad de qpdf: es una capacidad legítima mal delegada.

## Cuándo aplica

- `sudo -l` permite `/usr/bin/qpdf` como cualquier usuario; puede pedir la contraseña del usuario.
- El usuario puede leer el PDF resultante.
- Hay archivos sensibles legibles por root.

## Procedimiento

1. Confirmar la regla de sudo y la versión.
2. Crear un PDF vacío con `--empty`.
3. Añadir el archivo objetivo con `--add-attachment`.
4. Cerrar las opciones con `--` antes del nombre de salida.
5. Extraer o abrir el adjunto.

## Comandos

```bash
sudo qpdf --empty --add-attachment /root/.ssh/id_rsa -- out.pdf
qpdf --show-attachment=id_rsa out.pdf
qpdf --list-attachments out.pdf
```

## Variantes

- Adjuntar `/etc/shadow` o `/root/root.txt`.
- Usar `--replace-input` para sobrescribir un PDF existente.
- Encadenar con `scp` para exfiltrar el PDF.
- Añadir varios archivos en una sola ejecución.

## Limitaciones

- qpdf necesita `--` para terminar las opciones del adjunto.
- El archivo debe existir y ser legible por root.
- El PDF resultante debe poder leerse o copiarse.
- Algunas reglas de sudo limitan los argumentos permitidos.

## Mitigación

- No delegar qpdf sin argumentos a usuarios no administradores.
- Usar una regla de sudo con un wrapper y una lista blanca.
- Restringir la lectura de claves y archivos de root.
- Auditar los PDFs generados y sus adjuntos.

## Detección

- `qpdf --add-attachment` en procesos con UID 0.
- PDFs creados en `/tmp` o `/dev/shm` por usuarios normales.
- Lecturas de `/root/.ssh` desde procesos qpdf.
- Reglas de sudo que permiten binarios genéricos.

## Referencias

- [qpdf — Manual](https://qpdf.readthedocs.io/)
- [qpdf — Embedded files](https://qpdf.readthedocs.io/en/stable/cli.html#embedded-files)
- [0xdf — IClean](https://0xdf.gitlab.io/2024/08/03/htb-iclean.html)
