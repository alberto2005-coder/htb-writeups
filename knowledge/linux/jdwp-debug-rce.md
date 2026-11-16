---
topic: JDWP — ejecución remota a través del depurador de Java
tags: [linux, java, jdwp, debug, rce, privesc]
---

# JDWP — ejecución remota a través del depurador de Java

[🌐 English](jdwp-debug-rce.en.md) | **Español**

## Concepto

JDWP (Java Debug Wire Protocol) es el protocolo que usa un JVM con `-agentlib:jdwp` para aceptar un depurador. No tiene autenticación: quien se conecta puede inspeccionar clases, crear objetos y llamar a `Runtime.exec()` en el contexto del proceso. Si el JVM corre como root, la conexión es root.

## Cuándo aplica

- `ps` muestra `-agentlib:jdwp=transport=dt_socket,server=y,address=...`.
- El puerto está en `localhost` pero hay SSH, un proxy o SSRF.
- El proceso Java tiene privilegios altos.

## Procedimiento

1. Localizar el puerto real del depurador en la línea de comandos (por ejemplo, `8000`).
2. Confirmar que acepta conexiones (`nc`, `jdb` o el script).
3. Crear un script con la reverse shell en disco.
4. Ejecutar `jdwp-shellifier` con `--cmd` apuntando al script.
5. Recibir la conexión en el listener.

## Comandos

```bash
ps auxww | grep -- '-agentlib:jdwp'
ssh -L 223:localhost:8000 user@<IP>
python3 jdwp-shellifier.py -t 127.0.0.1 -p 223 --cmd '/dev/shm/x.sh'
```

`223` es el puerto local del túnel; el JVM sigue escuchando en `8000`.

## Variantes

- `jdb` interactivo con `print new java.io.File(...)`.
- Conexión directa si el puerto está expuesto.
- Puerto alcanzable por SSRF o por un proxy inverso.
- Shell en memoria con una clase Java en lugar de un script.

## Limitaciones

- El depurador debe estar habilitado y escuchando.
- Algunas versiones exigen un handshake o suspenden el proceso.
- Un firewall puede bloquear el puerto aunque esté en `localhost`.
- El script debe ser ejecutable por el usuario del JVM.

## Mitigación

- No habilitar JDWP en producción.
- Si se necesita depuración, usar un socket local con ACL y túneles autenticados.
- Ejecutar la JVM con un usuario sin privilegios.
- Monitorizar la presencia de `jdwp` en procesos.

## Detección

- Líneas de proceso con `-agentlib:jdwp`.
- Conexiones entrantes al puerto de depuración.
- Creación de procesos hijos desde la JVM.
- Lectura de scripts en `/dev/shm` por parte de Java.

## Referencias

- [Oracle — JPDA](https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/)
- [IOActive — jdwp-shellifier](https://github.com/IOActive/jdwp-shellifier)
- [0xdf — AI](https://0xdf.gitlab.io/2020/01/25/htb-ai.html)
