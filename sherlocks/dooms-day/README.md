---
sherlock: dOOMs Day
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, web, php, php2shell, cve-2026-109618, cve-2026-109619, log-analysis]
---

# dOOMs Day — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un servidor Apache con **PHP 8.4.26** acumula caídas de workers y un proceso hijo que no debería existir. Se entregan `access.log`, `error.log` y una captura; el objetivo es reconstruir la explotación de **PHP2Shell** (CVE-2026-109618 / CVE-2026-109619), que no toca la aplicación: vive en el parser de multipart de PHP.

## Evidencias

- `logs/access.log` y `logs/error.log` de Apache.
- `capture.pcap` del periodo.

## Investigación

### 1. Agotamiento de workers

```bash
grep AH00161 "logs/error.log" | wc -l
```

Apache avisa de que no quedan hijos disponibles decenas de veces con un único cliente: el atacante mantiene subidas `multipart` estancadas hasta ocupar todo el pool (149 de 150 con la configuración por defecto).

### 2. El OOM que no es un crash

```bash
grep -m1 "Allowed memory size" "logs/error.log"
```

El límite por defecto (`128M` = `134217728` bytes) se cruza a propósito. Cuando ZendMM no puede reservar no devuelve `NULL`: llama a `zend_bailout` (`longjmp`), se salta el *teardown* del request y deja punteros de sesión colgando. El worker sigue vivo y reutiliza ese estado sucio en la petición siguiente: es la primitiva de use-after-free.

### 3. Las dos CVEs

- **CVE-2026-109618**: corrupción por agotamiento de memoria durante el parseo, antes de ejecutar el script.
- **CVE-2026-109619**: estado global obsoleto que sobrevive a la memoria del request.

Se corrigen en PHP **8.4.27** (y 8.2.35 / 8.3.36 / 8.5.12). El campo que las activa es `PHP_SESSION_UPLOAD_PROGRESS`, procesado en `main/rfc1867.c` antes de la aplicación: por eso el `access.log` casi no dice nada y todo está en `error.log`.

### 4. Fuga de ASLR por la respuesta

La sesión colgante se reocupa con una cabecera falsa y PHP escribe ~600 KB de heap vecino en `Set-Cookie: PHPSESSID=...`; de ahí salen las bases de `libphp.so` y del chunk. Señal en el log de acceso: `Set-Cookie` de cientos de KB.

```bash
awk '{print length($0)}' logs/access.log | sort -rn | head
```

### 5. Post-explotación

Con las bases conocidas se forja un `zend_array` cuyo `pDestructor` apunta a `zif_system` y se obtiene ejecución como `www-data`. En el PCAP se ve la reverse shell al **4444**; en el host, procesos hijos del worker (`sh -c ...`), no del binario final.

## Conclusiones

Compromiso sin autenticar y sin tocar la aplicación: el vector es el runtime PHP (`session.upload_progress`) y la evidencia está en `error.log` (workers agotados + OOM), no en los logs de la web.

## Lecciones

- Un fatal por memoria no es un crash: es un `longjmp` que puede dejar estado reutilizable.
- La explotación ocurre **antes** del script: funciona incluso en una página sin PHP.
- El `error.log` es el artefacto principal; el `access.log` solo da el cliente y el tamaño.

## Mitigaciones y detección

- `session.upload_progress.enabled = Off` si no se usan barras de progreso: una línea y no rompe nada.
- Actualizar a PHP 8.4.27+ (8.2.35 / 8.3.36 / 8.5.12).
- `memory_limit` realista y `MaxRequestWorkers` acorde al contenedor.
- Alertas: `AH00161` repetido con un solo cliente, `Allowed memory size` seguido de un hijo del worker, `Set-Cookie` de cientos de KB, `PHP_SESSION_UPLOAD_PROGRESS` en el cuerpo.
