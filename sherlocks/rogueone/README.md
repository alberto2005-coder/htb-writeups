---
sherlock: RogueOne
domain: DFIR / Memoria
difficulty: Medium
platform: Hack The Box
evidence: Volcado de memoria de un puesto de Forela
tools: [Volatility 3, windows.netscan, windows.cmdline, strings]
---

# RogueOne — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El SIEM dispara varias alertas en menos de un minuto señalando posible **C2** desde el puesto de Simon Stark (Forela). No hay procesos sospechosos visibles, así que el SOC aísla la máquina y entrega un volcado de memoria para confirmar el canal y reconstruir la línea temporal.

## Evidencia

- Un único fichero: volcado de memoria de Windows (`20230810.mem`).

## Método

1. **Perfil del volcado** y lista de procesos: se buscan huérfanos, procesos con nombre legítimo pero ruta rara y relaciones padre-hijo anómalas.

```bash
vol -f 20230810.mem windows.pslist
vol -f 20230810.mem windows.pstree
```

2. **Conexiones de red** — el plugin que resuelve el caso:

```bash
vol -f 20230810.mem windows.netscan | grep <PID>
```

Devuelve una conexión desde el PID sospechoso a una IP externa en un puerto alto (en esta máquina, `13.127.155.166:8888`).

3. **Línea de comandos** del proceso para ver con qué se lanzó y desde dónde:

```bash
vol -f 20230810.mem windows.cmdline --pid <PID>
```

4. **Hora de ejecución**: `windows.netscan` y los tiempos de creación del proceso (`pslist` con `--physical`) dan el instante en que se estableció el canal.

5. **Huella del binario**: si se puede volcar el ejecutable del proceso, `strings`/hash MD5 lo identifican y permiten buscarlo en inteligencia.

## Qué enseña

- Un volcado de memoria demuestra C2 aunque el EDR no vea procesos raros: `netscan` es la evidencia primaria.
- La relación padre-hijo y la ruta del binario delatan el dropper.
- La línea temporal se arma cruzando creación del proceso y primer paquete del canal.

## Tropiezos

- **Perfiles**: Volatility 3 no necesita perfil, pero algunos plugins fallan con volcados truncados.
- **Puertos efímeros**: filtrar por PID en lugar de por puerto evita ruido de actualizaciones y telemetría.
- **Procesos con nombre legítimo**: aquí el nombre no canta; la anomalía está en la ruta y en la conexión saliente.
