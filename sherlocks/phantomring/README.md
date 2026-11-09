---
sherlock: PhantomRing
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, linux, elf, reverse-engineering, ghidra, c2]
---

# PhantomRing — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; sin respuestas literales de la plataforma.

## Escenario

Una alerta señaló actividad extraña en un servidor Linux. El analista anterior dejó una muestra: un binario ELF ejecutado desde `/var/tmp` que parece mantener comunicación con el exterior. Hay que caracterizarlo: qué hace, con quién habla y cómo se camufla.

## Evidencias

- Muestra ELF (sin empaquetar y sin símbolos, pero no ofuscada en exceso).
- Metadatos del host: ruta de ejecución, usuario que lo lanzó, hora.
- Opcionalmente, captura del tráfico.

## Investigación

### 1. Triaje estático

Nunca en la máquina de análisis sin aislamiento; aquí basta con no ejecutarlo.

```bash
file phantom
sha256sum phantom
readelf -h phantom
strings -n 6 phantom | less
```

`file` confirma arquitectura y enlazado (estático o dinámico). `strings` suele dar la primera pista: URLs, dominios, rutas de persistencia y mensajes de error del propio autor.

### 2. Importaciones y comportamiento

```bash
readelf -s phantom | grep -E "UND|FUNC"
objdump -d -M intel phantom | less
```

La lista de símbolos importados dice casi todo: `socket`, `connect`, `getaddrinfo` apuntan a C2; `fork`, `setsid`, `daemon` a demonización; `chmod`, `unlink` a limpieza de huellas.

### 3. Descompilar con Ghidra

Se importa el binario, se deja el analizador automático y se buscan las referencias a las cadenas interesantes (`Search > For Strings`, luego `References`). El `main` suele mostrar:

1. Comprobación de argumentos / entorno.
2. Conexión al host remoto con un token o cabecera fija.
3. Bucle de lectura de comandos y ejecución (`popen`/`system`).
4. Rutina de persistencia opcional.

Con el seudocódigo se reconstruye el protocolo (qué se envía primero, cómo se identifica el implante, qué formato tienen las respuestas).

### 4. Correlación con el host

```bash
ls -la /var/tmp
grep -R "phantom" /etc/cron* /etc/systemd 2>/dev/null
```

La ruta de ejecución y el usuario permiten responder si el implante corría como servicio, por cron o a mano. Los IOC salen de aquí: hash, ruta, nombre del proceso, dominio/IP de C2.

## Conclusiones

- Implante tipo *backdoor* con C2 por socket y ejecución de comandos.
- Se ejecuta desde un directorio temporal escribible, práctica habitual para pasar desapercibido.
- El análisis estático basta para extraer C2, protocolo e IOC; no hace falta detonarlo.

## Lecciones

- `/var/tmp` y `/dev/shm` ejecutables son un indicador de por sí.
- `strings` + importaciones resuelven la mitad de un binario pequeño antes de abrir el descompilador.
- Documentar IOC (hash, ruta, C2, proceso) es el entregable real, no el seudocódigo.
