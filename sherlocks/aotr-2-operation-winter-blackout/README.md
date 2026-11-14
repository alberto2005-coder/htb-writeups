---
sherlock: "AoTR 2: Operation Winter Blackout"
category: Threat Intelligence
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [threat-intelligence, forum, phishing, infrastructure, osint]
---

# AoTR 2: Operation Winter Blackout — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Tras el compromiso de una empresa logística, los investigadores acceden a un foro privado usado por el grupo. El foro contiene conversaciones sobre una operación llamada Winter Blackout. Se pide identificar a los miembros, la infraestructura y el objetivo.

## Evidencias

- Exportación del foro y credenciales obtenidas en la investigación anterior.
- Perfiles, mensajes, imágenes y direcciones de infraestructura.
- Registros de acceso al foro y metadatos de los archivos.

```bash
sha256sum forum-export.zip
unzip -l forum-export.zip
```

## Investigación

### 1. Inventario y triaje

Se catalogan usuarios, roles, hilos y archivos adjuntos. Los alias y las firmas permiten agrupar mensajes. Se anotan las fechas y se normalizan las zonas horarias.

```bash
grep -RInE 'Curator|Bellringer|SnowFox|Driver_BUD|Ledger' forum/
```

### 2. Línea temporal

Los mensajes muestran la planificación: reconocimiento, elección del objetivo, compra de infraestructura y reglas de OPSEC. Se ordenan por fecha y se cruzan con los dominios y cuentas mencionadas.

### 3. Artefacto clave

Las imágenes y los enlaces revelan geolocalización, proveedores y nombres reales. Un alias filtra un nombre en una conversación casual; otro publica una captura con metadatos. La combinación permite atribuir roles y anticipar el siguiente paso.

## Conclusiones

- El grupo tiene al menos cinco miembros con roles diferenciados.
- La operación se dirige a una empresa logística concreta.
- La infraestructura usa dominios y cuentas reutilizadas.
- La mala OPSEC del foro permite atribución parcial.

## Lecciones

- Un foro privado es una fuente de inteligencia, no solo de malware.
- Los alias deben correlacionarse con horarios, estilo y metadatos.
- Las imágenes pueden filtrar ubicación y nombres.
- La inteligencia de amenazas requiere citar la fuente y separar inferencia de hecho.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://medium.com/@andrginting/hackthebox-aotr-2-operation-winter-black-bfb559d9f945>
- <https://attack.mitre.org/resources/centers/intel/>
