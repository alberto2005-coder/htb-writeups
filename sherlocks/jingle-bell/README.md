---
sherlock: Jingle Bell
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Base de datos de notificaciones de Windows de un puesto
tools: [DB Browser for SQLite, strings, SQLite]
state: Retired
tags: [dfir, dfir-/-windows]
---


# Jingle Bell — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Torrin es sospechoso de filtrar datos de Forela y de instalar software no autorizado. El equipo forense no encontró la fuga en los artefactos habituales, así que la evidencia que queda es la **base de datos de notificaciones** del propio Windows.

## Evidencias

- Copia del perfil: `AppData\Local\Microsoft\Windows\Notifications\` (base `WPNDatabase.db` y sus ficheros asociados).

## Investigación

1. **Abrir la base con SQLite**: es un SQLite normal.

```bash
sqlite3 WPNDatabase.db '.tables'
sqlite3 WPNDatabase.db '.schema Notification'
```

2. **Leer la tabla `Notification`**: cada fila es una notificación *toast* con su aplicación de origen, el payload y la hora. Ahí queda el rastro de la conversación.

```sql
SELECT Id, HandlerId, Payload, ArrivalTime FROM Notification;
```

3. **Interpretar el payload**: el XML interno trae el remitente, el texto y a veces adjuntos. Se identifican dos partes: el usuario de Forela y su interlocutor externo.

4. **Software no autorizado**: el `HandlerId`/`Handler` revela qué aplicación generó cada notificación; una app de mensajería o de transferencia que no es corporativa responde a la pregunta de qué usó para filtrar.

5. **Cronología**: ordenar por `ArrivalTime` y encajar la conversación (quién propone, quién acepta, cuánto se paga).

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- Las notificaciones de Windows guardan **contenido de mensajes** que el usuario ya vio: es evidencia de comunicaciones.
- Una app de mensajería deja rastro aunque se desinstale: la base de notificaciones sobrevive en el perfil.
- El `HandlerId` identifica la aplicación sin necesidad de ejecutarla.

## Tropiezos

- **Base bloqueada**: copiar `WPNDatabase.db` junto con sus `-wal`/`-shm` para no perder filas recientes.
- **Payload XML**: el texto va escapado; conviene formatearlo antes de leerlo.
- **Varias cuentas**: filtrar por el SID del usuario investigado.
