---
topic: SRUM y bases ESE en Windows
tags: [forensics, windows, srum, ese, network, edb]
---

# SRUM y bases ESE en Windows

[🐬 English](srum-ese.en.md) | **Español**

## Concepto

System Resource Usage Monitor (SRUM) registra consumo de CPU, red y aplicación por proceso en `SRUDB.dat`. Es una base ESE; `SrumECmd` la procesa y permite estimar qué proceso envió datos y cuándo.

## Cuándo aplica

- Faltan logs de firewall o proxy.
- Se busca el proceso responsable de tráfico saliente.
- Se quiere una ventana temporal de ejecución.

## Procedimiento

1. Copiar `SRUDB.dat` y el registro asociado.
2. Procesar con `SrumECmd`.
3. Filtrar por proceso y bytes enviados/recibidos.
4. Cruzar con prefetch y MFT.
5. Estimar el volumen y la ventana.

```bash
SrumECmd.exe -f SRUDB.dat --csv srum
```

## Variantes

- `Windows.edb` para búsquedas e índices.
- `SRUDB.dat` de servidores y estaciones.
- Correlación con eventos 5156.

## Limitaciones

- SRUM no guarda contenido ni destinos.
- La base puede estar bloqueada; usar copia.
- Los contadores son acumulativos y pueden redondear.

## Mitigación

- Centralizar logs de red.
- Proteger y retener las bases ESE.
- Monitorizar procesos con tráfico anómalo.

## Detección

- Picos de bytes por proceso.
- Procesos de usuario con tráfico alto.
- Correlación con conexiones de C2.

## Referencias

- <https://github.com/EricZimmerman/Srum>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://www.hackthebox.com/sherlocks>
