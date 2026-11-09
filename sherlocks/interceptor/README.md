---
sherlock: Interceptor
domain: SOC / Red
difficulty: Easy
platform: Hack The Box
evidence: Captura de tráfico de una infección con SSLoad
tools: [Wireshark, tshark, CyberChef, Python]
---

# Interceptor — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un SOC detecta actividad sospechosa hacia Internet. La captura contiene la infección completa de un cargador tipo **SSLoad**: descarga de un **MSI** por **WebDAV**, ejecución y comunicación **C2 cifrada con RC4**.

## Evidencia

- Un PCAP con tráfico web, WebDAV y conexiones salientes.

## Método

1. **Descarga inicial**: buscar peticiones a recursos `.msi` y métodos WebDAV (`PROPFIND`, `OPTIONS`, `GET` con `Depth`).

```bash
tshark -r interceptor.pcap -Y 'http.request' -T fields -e http.host -e http.request.method -e http.request.uri
```

2. **Cadena de ejecución**: el MSI lanza `msiexec` y deja un binario o script; en Sysmon/EDR se vería el padre, aquí se infiere del tráfico y del contenido descargado.

3. **C2**: identificar el host y el patrón (POST con cuerpo binario, `User-Agent` propio, intervalos regulares).

4. **Descifrar**: el cuerpo va **RC4**; la clave suele estar en el propio binario o derivarse del `User-Agent`/URI. Probar clave del payload con CyberChef.

```bash
tshark -r interceptor.pcap -Y 'http.request.method=="POST"' -T fields -e http.host -e tcp.payload | head
```

5. **Extraer el siguiente stage**: del JSON descifrado salen comandos, rutas y URLs nuevas. Documentar IOCs.

## Qué enseña

- WebDAV se usa para entregar cargas porque muchas redes permiten el método y el filtrado no lo inspecciona.
- Un MSI firmado o no, ejecutado por el usuario, es ejecución de código sin explotar nada.
- El C2 en RC4 tiene un patrón claro: cuerpos de longitud fija y alta entropía.

## Tropiezos

- **Tráfico TLS**: si la descarga va cifrada, sólo quedan SNI, tamaños y horas.
- **Clave del RC4**: sin la muestra del cargador, hay que probar candidatos del propio tráfico.
- **Ruido de actualizaciones**: separar por `User-Agent` y por destino antes de leer cuerpos.
