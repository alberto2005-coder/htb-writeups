---
sherlock: PhantomRing
domain: Análisis de malware / Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, linux, elf, reverse-engineering, ghidra, c2]
---

# PhantomRing — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; sin respuestas literales de la plataforma.

## Escenario

Una alerta señaló actividad extraña en un servidor Linux. El analista anterior dejó una muestra: un **ELF** ejecutado desde `/var/tmp` que mantiene comunicación con el exterior. Hay que caracterizarlo sin detonarlo: qué hace, con quién habla y cómo se camufla.

## Evidencias

```text
phantomring.zip        (contraseña en la página del Sherlock)
  └── phantom_ring/agent
```

## Investigación

### 1. Triaje estático

```bash
file phantom_ring/agent
sha256sum phantom_ring/agent
readelf -h phantom_ring/agent
strings -n 6 phantom_ring/agent | less
```

Es un **ELF x86-64 PIE, enlazado dinámicamente** con intérprete `/lib64/ld-linux-x86-64.so.2`, sin empaquetar y **sin `strip`**: eso cambia la estrategia, porque los nombres reales de las funciones siguen ahí.

```bash
nm phantom_ring/agent | grep ' T \| t '
```

### 2. Símbolos: el atajo

Con el binario sin *strippear*, `nm` devuelve funciones con nombre en lugar de `sub_401230`. Buscar las que huelen a red, a persistencia y a ejecución de comandos reduce el análisis a unos minutos:

```bash
nm phantom_ring/agent | grep -iE 'connect|socket|exec|persist|cmd|port'
objdump -d -M intel --disassemble=<funcion> phantom_ring/agent | less
```

### 3. El puerto de C2

El puerto no está en una tabla ni cifrado: aparece como **operando inmediato** de la instrucción que prepara la estructura de `connect`. Convertido de hexadecimal a decimal es la respuesta, sin necesidad de ejecutar nada.

### 4. Comportamiento

Con `Ghidra` (o `objdump`) se reconstruye el flujo: comprobación de entorno, conexión al host remoto, bucle de lectura de comandos y ejecución (`system`/`popen`), más una rutina opcional de persistencia. Los IOC salen de aquí: hash SHA-256, ruta `/var/tmp`, nombre del proceso y endpoint de C2.

### 5. Correlación con el host

```bash
ls -la /var/tmp
grep -R "agent" /etc/cron* /etc/systemd 2>/dev/null
```

La ruta y el usuario de ejecución dicen si corría como servicio, por cron o a mano.

## Conclusiones

- Implante tipo *backdoor*: C2 por socket y ejecución de comandos en el host.
- Se ejecuta desde un directorio temporal escribible, práctica habitual para no tocar rutas vigiladas.
- El análisis estático basta para extraer C2, protocolo e IOC; el binario nunca se ejecuta.

## Lecciones

- `/var/tmp` y `/dev/shm` ejecutables son un indicador por sí mismos.
- Un binario **sin `strip`** regala los nombres de función: empieza por `nm`, no por el descompilador.
- `strings` + símbolos resuelven la mitad de un binario pequeño; el puerto suele estar como inmediato en el código.
- Documentar hash, ruta y endpoint convierte el análisis en algo accionable para el equipo de detección.
