---
sherlock: Jingle Bell
domain: DFIR / Windows
difficulty: Easy
platform: Hack The Box
evidence: Base de datos de notificaciones de Windows de un puesto
tools: [DB Browser for SQLite, strings, SQLite]
state: Retired
tags: [dfir, windows, notifications, wpndatabase, slack, insider-threat]
---

# Jingle Bell — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Torrin es sospechoso de filtrar datos de Forela y de instalar software no autorizado. El equipo forense no encontró la fuga en los artefactos habituales, así que la evidencia que queda es la **base de datos de notificaciones** del propio Windows.

## Evidencias

- `Torrincase/C/Users/<usuario>/AppData/Local/Microsoft/Windows/Notifications/wpndatabase.db` y sus acompañantes `-wal` y `-shm`.

## Investigación

1. **Abrir la base**: es SQLite normal; hay que copiar los tres ficheros juntos para que el WAL se fusione.

```bash
sqlite3 wpndatabase.db '.tables'
sqlite3 wpndatabase.db '.schema Notification'
```

2. **La tabla `Notification`**: cada fila es un *toast* con `Payload` (el XML que se mostró), `ArrivalTime` (FILETIME de Windows) y `HandlerId`, que apunta a `NotificationHandler` para saber qué aplicación lo generó.

```sql
SELECT Id, HandlerId, ArrivalTime, Payload FROM Notification;
```

3. **La aplicación**: `NotificationHandler` identifica **Slack** como origen de los toasts. Ese es el software no corporativo que usó para la fuga, y explica por qué no quedaba rastro en los artefactos clásicos.

4. **La conversación**: el XML del `Payload` trae remitente y texto. Ordenando por hora aparece el intercambio completo con la otra parte (una empresa externa), incluida la propuesta, la entrega y el pago.

5. **Cuidado con la hora**: `ArrivalTime` es cuándo Windows mostró el aviso, no cuándo se envió el mensaje. Si la pregunta pide la hora del mensaje, hay que sacarla del enlace de lanzamiento del toast, no de esa columna.

## Conclusiones

Torrin filtró información de Forela por **Slack**. La base de notificaciones conservó el contenido de los mensajes que ya se habían mostrado en pantalla, incluso sin la aplicación ni sus logs.

## Lecciones

- Las notificaciones de Windows guardan **contenido de mensajes** que el usuario ya vio: es evidencia de comunicaciones.
- Una app de mensajería deja rastro aunque se desinstale: la base de notificaciones sobrevive en el perfil.
- `HandlerId` identifica la aplicación sin necesidad de ejecutarla.
- `Payload` es XML escapado: formatearlo antes de leerlo.

## Qué enseña

- Los artefactos "menores" del perfil (notificaciones, Jump Lists, Activity) resuelven casos que el correo y el disco no explican.
- `ArrivalTime` y la hora del mensaje son cosas distintas; confundirlas arruina la línea temporal.
- Un insider puede no dejar correo: la notificación del chat sí queda.

## Tropiezos

- **Base bloqueada**: copiar `wpndatabase.db` con `-wal`/`-shm`; sin ellos se pierden las filas recientes.
- **Varias cuentas**: filtrar por el SID del usuario investigado.
- **XML**: el texto va escapado y con etiquetas de la app; conviene extraer solo el cuerpo.
