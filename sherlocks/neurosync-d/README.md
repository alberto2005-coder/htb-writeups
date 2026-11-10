---
sherlock: NeuroSync-D
domain: DFIR / Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, nextjs, cve-2025-29927, ssrf, lfi, redis, bci]
---

# NeuroSync-D — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

NeuroSync fabrica dispositivos BCI (interfaz cerebro-ordenador) y su web corre sobre **Next.js**. Un grupo APT ha entrado y se mueve lateralmente; parte de los dispositivos en línea quedaron bajo su control explotando un *N-day*. Hay que emular la cadena ofensiva y después explicarla con los logs.

## Evidencias

```text
NeuroSync/
├── interface.log      (stdout de Next.js: arranque y una línea por petición)
├── access.log         (frontend)
├── data-api.log       (API interna)
├── redis.log          (cola de trabajos)
└── bci-device.log     (comunicación con el hardware)
```

## Investigación

### 1. Versión y CVE

`interface.log` arranca con el banner de Next.js (`Local: http://localhost:3000`) y registra el `User-Agent` y los códigos de cada request. La versión es anterior al parche de **CVE-2025-29927**: bypass de autorización del *middleware* enviando la cabecera interna repetida.

```bash
grep -h "Local:" interface.log
grep -i "x-middleware-subrequest" interface.log | head
# x-middleware-subrequest: middleware:middleware:middleware:middleware:middleware
```

### 2. Reconocimiento web

`access.log` muestra primero peticiones a ficheros estáticos típicos de Next.js para identificar la build (`main-app.js`, `_buildManifest.js`), con `200`, y después el endpoint vulnerable con la cabecera del bypass.

### 3. SSRF y API interna

Con el middleware saltado, el atacante fuerza al servidor a pedir direcciones internas y descubre una **API en el puerto 4000**. `data-api.log` conserva el escaneo y las peticiones posteriores.

### 4. LFI y secretos

La API expone un endpoint de lectura de logs vulnerable a *path traversal*: primero `/etc/passwd`, después su propio código fuente y un fichero de **secreto** (`secrets.txt`). Con la clave de firma se pueden fabricar mensajes que la cola acepta.

### 5. RCE por inyección en Redis

La aplicación consume trabajos de **Redis**. El atacante publica un comando firmado que, al decodificarse, ejecuta una descarga y ejecución contra un host externo; `bci-device.log` y `redis.log` registran el efecto en el dispositivo.

## Conclusiones

- Entrada: **CVE-2025-29927** en el middleware de Next.js.
- Reconocimiento: SSRF para mapear la red interna y localizar la API del 4000.
- Datos: LFI del endpoint de logs hasta el código y el secreto de firma.
- Impacto: inyección en la cola Redis → ejecución en el dispositivo BCI.

## Lecciones

- Un bypass de middleware no necesita payload exótico: la cabecera interna repetida basta.
- Los logs de aplicación (`interface.log`) y de la API (`data-api.log`) hay que cruzarlos: cada uno ve una mitad.
- Un secreto en el servidor web es una llave para cualquier servicio que firme con él.
- Mitigación: parchear Next.js (>= 15.2.3 / 14.2.25 / 13.5.9 / 12.3.5), filtrar cabeceras internas en el borde, no exponer APIs en redes planas y autenticar la cola Redis.
