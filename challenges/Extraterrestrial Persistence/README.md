---
challenge: Extraterrestrial Persistence
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, linux, systemd, persistence, base64]
type: Forensics
---

# Extraterrestrial Persistence — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un script de shell instala persistencia en Linux: se descarga un binario a `/usr/local/bin/service`, crea una **unidad de systemd** a partir de un bloque **base64** y la habilita. Al decodificar el bloque aparece el `.service`, y su `Description` contiene la flag.

## Enunciado y superficie

«There is a rumor that aliens have developed a persistence mechanism that is impossible to detect». Se entrega `persistence.sh`, un script de instalación de persistencia para Linux.

## Reconocimiento

```bash
file persistence.sh
cat persistence.sh
```

El script comprueba `whoami`/`hostname` (`pandora` y `linux_HQ`), descarga un binario con `curl` a `/usr/local/bin/service`, lo hace ejecutable y escribe una unidad de systemd desde base64.

## Análisis del código

La unidad se crea con `echo -e "<base64>" | base64 --decode > /usr/lib/systemd/system/service.service` y se activa con `systemctl enable`. El bloque base64 es el único punto interesante del script.

## Explicación del fallo

No hay vulnerabilidad: es una cadena de instalación. El script se autolimita al host víctima, descarga el payload y registra un servicio que se ejecuta en cada arranque. La flag está escondida en el campo `Description` de la unidad, no en el binario.

## Reproducción local

```bash
grep -o '"[A-Za-z0-9+/=]\{40,\}"' persistence.sh | tr -d '"' | base64 -d
```

Se decodifica el bloque sin ejecutar el script; no hace falta systemd.

## Explotación

1. Leer el script y localizar el `echo -e` con base64. 2. Decodificarlo. 3. Leer `Description=`.

## Evidencia

- `persistence.sh`.

## Lecciones aprendidas

- **`echo -e`**: puede haber saltos de línea escapados; decodificar con `base64 -d` desde fichero evita problemas.
- **Doble codificación**: si el texto decodificado no empieza por `[Unit]`, hay otra capa.
- **No ejecutarlo**: el análisis es estático; ejecutar el script descarga y activa un binario.

- Los scripts de persistencia suelen incluir su propio instalador; leerlo da el mecanismo completo.
- `base64` en un `echo` es ofuscación trivial: una línea la deshace.
- Una unidad systemd con `oneshot` y `RemainAfterExit` es persistencia silenciosa.

## Mitigaciones y detección

- Monitorizar `/usr/lib/systemd/system` y `systemctl enable` fuera de despliegues: una unidad nueva es persistencia.
- Alertar de descargas a `/usr/local/bin` desde dominios que imitan repositorios (`files.pypi-install.com` no es PyPI).
- EDR: procesos `curl` seguidos de `chmod +x` y `systemctl` en el mismo árbol.

## Referencias

- [systemd-timers](../../knowledge/privesc/systemd-timers.md)
## Método

1. **Leer el script**: primero comprueba `whoami`/`hostname` para ejecutarse sólo en el host esperado; después descarga y prepara la unidad.

```bash
cat persistence.sh
```

2. **Localizar el bloque**: hay un `echo -e "<base64>" | base64 --decode > /usr/lib/systemd/system/service.service`.

3. **Decodificar** sin ejecutar nada:

```bash
echo '<base64>' | base64 -d
```

```ini
[Unit]
Description=<flag>
After=network.target network-online.target
...
```

4. **Interpretar la persistencia**: `Type=oneshot` con `RemainAfterExit=yes` y `WantedBy=multi-user.target` hace que el binario se ejecute en cada arranque; `systemctl enable` crea el enlace.
