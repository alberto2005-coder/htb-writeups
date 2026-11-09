---
sherlock: Loggy
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, logs, web-server, access-log, triage]
---

# Loggy — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un servidor web genera alertas por peticiones extrañas. Se entrega un conjunto de logs de aplicación y de sistema; hay que identificar la actividad maliciosa, el recurso objetivo y si hubo éxito.

## Evidencias

- `access.log` y `error.log`.
- Logs de autenticación del mismo periodo.
- Configuración del servidor (vhosts, rutas).

## Investigación

### 1. Normalizar el formato

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -20
```

Con el top de IPs y de rutas se separa el ruido de escáneres del atacante real: pocas peticiones, muy dirigidas, `User-Agent` de herramienta.

### 2. Buscar el patrón de ataque

```bash
grep -Ei "union|select|\.\./|/etc/passwd|cmd=|shell|\.env" access.log | head -30
```

Se clasifica lo encontrado: traversal, inyección, subida de fichero, escaneo de rutas. El código de respuesta dice si funcionó: `200` donde debería haber `403` es la señal.

### 3. Cerrar la ventana

```bash
grep "<IP_ATACANTE>" access.log | awk '{print $4, $6, $7, $9}' | head -40
```

La secuencia completa (reconocimiento → exploit → acceso a recurso) ordenada por hora es la respuesta. Se comprueba si hay peticiones posteriores desde la misma IP a otros vhosts.

## Conclusiones

- Actividad dirigida contra un recurso concreto del servidor web.
- La diferencia entre intento y compromiso está en los códigos de estado y en el tamaño de la respuesta.
- Los escáneres automáticos del resto del log son ruido de fondo.

## Lecciones

- `awk` + `sort | uniq -c` resuelve la mitad de un caso de logs antes de abrir nada más.
- Comparar tamaño de respuesta (`$10`) delata extracciones de datos que un `200` solo no muestra.
- Un log sin reloj sincronizado no sirve para correlacionar: NTP también es forense.
