---
machine: Analysis
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, ldap, active-directory, webshell, hta, snort, privesc]
---

# Analysis — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio PHP de `analysis.htb` consulta Active Directory por LDAP con un parámetro controlable. La inyección LDAP permite enumerar usuarios y leer el campo `description` de una cuenta compartida, donde está la contraseña del panel interno. En el dashboard se sube una webshell PHP o un archivo HTA para ejecutar código como `svc_web`. Las credenciales de `jdoe` aparecen en los valores de autologon del registro y, como ruta alternativa, en los logs web de `alert_panel.php`. Con WinRM se llega a `jdoe`. Para Administrateur se escribe una DLL maliciosa en el directorio de preprocesadores dinámicos de Snort, que Snort carga con privilegios elevados.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985 <IP>
```

- `53`, `88`, `389`, `636`, `3268` y `3269`: DNS, Kerberos y LDAP de un controlador de dominio.
- `80`: IIS con el sitio principal.
- `445` y `139`: SMB.
- `5985`: WinRM, útil cuando se obtienen credenciales.
- El dominio es `analysis.htb` y el host `DC-ANALYSIS`.

```bash
echo '<IP> analysis.htb internal.analysis.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://analysis.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El sitio público es una página corporativa. El vhost `internal.analysis.htb` aloja un dashboard con un formulario que busca usuarios por nombre. La consulta se construye contra LDAP y el parámetro `name` acepta comodines: `name=b*` devuelve más resultados que `name=b`, lo que confirma que el `*` se interpreta dentro del filtro.

Con comodines se enumeran usuarios del dominio y se leen atributos como `description`. Una cuenta compartida guarda ahí su contraseña, que abre el dashboard interno.

## Foothold

El dashboard permite subir archivos. La vía directa es una webshell PHP en el directorio de subidas; la alternativa es un archivo HTA que se ejecuta al abrirse desde el panel. Cualquiera de las dos da ejecución como `svc_web` en `DC-ANALYSIS`.

```text
name=*
name=*)(description=*
```

La enumeración posterior del host muestra IIS, PHP y una instalación de Snort.

## Movimiento lateral

`svc_web` no puede leer los homes del resto de usuarios. Hay dos fuentes de credenciales para `jdoe`:

1. **Autologon:** en `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`, los valores `DefaultUserName` y `DefaultPassword` están en claro.
2. **Logs web:** `alert_panel.php` recibe usuario y contraseña por GET y los escribe en el log de IIS. El log de `W3SVC2` contiene las peticiones con las credenciales de `jdoe`.

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' |
  Select-Object DefaultDomainName, DefaultUserName, DefaultPassword
findstr alert_panel.php C:\inetpub\logs\LogFiles\W3SVC2\u_ncsa1.log
```

Con esas credenciales se abre una sesión de WinRM:

```bash
evil-winrm -i analysis.htb -u jdoe -p '<PASSWORD>'
```

## Escalada de privilegios

`C:\Snort\etc\snort.conf` carga preprocesadores dinámicos desde `C:\Snort\lib\snort_dynamicpreprocessor`. La ACL de esa carpeta permite a `BUILTIN\Users` crear archivos y directorios. Snort se ejecuta con privilegios elevados y carga las DLL del directorio, así que se compila una DLL que ejecuta una acción privilegiada y se coloca allí. Al recargar o reiniciar el servicio, la DLL se carga en el contexto de Snort y la elevación lleva a `Administrateur`.

```powershell
icacls C:\Snort\lib\snort_dynamicpreprocessor
# BUILTIN\Utilisateurs:(CI)(AD) y (WD)
```

## Evidencia

- Respuestas distintas al usar `*` en el parámetro `name`.
- Usuario y contraseña leídos del atributo `description`.
- Acceso al dashboard y ejecución de `whoami` como `svc_web`.
- Credenciales de `jdoe` en el registro y en el log de IIS.
- `whoami /priv` y sesión de WinRM como `jdoe`.
- ACL escribible del directorio de Snort y carga de la DLL.
- `whoami` como `administrateur`.

## Lecciones aprendidas

- Un filtro LDAP construido por concatenación permite enumerar todo el directorio.
- Los atributos `description` y `info` suelen contener secretos operativos.
- Las credenciales de autologon y los logs con parámetros GET son fugas habituales.
- Un directorio de plugins o preprocesadores escribible por usuarios es ejecución de código privilegiada.
- La subida de archivos debe validar extensión, contenido y destino, no solo el `Content-Type`.

## Mitigaciones y detección

- Parametrizar las consultas LDAP y escapar `*`, `(`, `)` y `\`.
- No guardar contraseñas en atributos del directorio; usar cuentas de servicio gestionadas.
- Restringir la lectura de `description` y auditar cambios.
- Deshabilitar el autologon con contraseña en claro o usar LSA secrets.
- No registrar credenciales en URLs; revisar los logs de IIS y limitar su acceso.
- Aplicar ACL mínimas a directorios de Snort, plugins y servicios.
- Alertar de escrituras de DLL en rutas de servicios y de cargas de Snort fuera de mantenimiento.

## Referencias

- [0xdf — Analysis](https://0xdf.gitlab.io/2024/06/01/htb-analysis.html)
- [IppSec — Analysis](https://www.youtube.com/watch?v=9U7OFdri73g)
- [Hack The Box — Analysis](https://app.hackthebox.com/machines/analysis)
- [Knowledge — Inyección LDAP en Active Directory](../../../knowledge/windows/ldap-injection-ad.md)
