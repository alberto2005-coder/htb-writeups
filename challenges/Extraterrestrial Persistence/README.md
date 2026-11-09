---
challenge: Extraterrestrial Persistence
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, linux, systemd, persistence, base64]
---

# Extraterrestrial Persistence — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un script de shell instala persistencia en Linux: se descarga un binario a `/usr/local/bin/service`, crea una **unidad de systemd** a partir de un bloque **base64** y la habilita. Al decodificar el bloque aparece el `.service`, y su `Description` contiene la flag.

## Evidencia

- `persistence.sh`.

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

## Tropiezos

- **`echo -e`**: puede haber saltos de línea escapados; decodificar con `base64 -d` desde fichero evita problemas.
- **Doble codificación**: si el texto decodificado no empieza por `[Unit]`, hay otra capa.
- **No ejecutarlo**: el análisis es estático; ejecutar el script descarga y activa un binario.

## Lecciones

- Los scripts de persistencia suelen incluir su propio instalador; leerlo da el mecanismo completo.
- `base64` en un `echo` es ofuscación trivial: una línea la deshace.
- Una unidad systemd con `oneshot` y `RemainAfterExit` es persistencia silenciosa.
