---
sherlock: Jinkies
domain: DFIR
difficulty: Medium
platform: Hack The Box
evidence: Triaje KAPE (TriageData + LiveResponse) de una estación con fuga de propiedad intelectual
tools: [EvtxECmd, MFTECmd, Chainsaw, Registry Explorer, secretsdump]
state: Active
tags: [dfir, windows, kape, smb, credential-reuse, exfiltration, t1021.002]
---

# Jinkies — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Active. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Cloud-Guru investiga la filtración de un diseño propietario. El sospechoso es un empleado que tenía acceso legítimo a un share de ingeniería. Se entrega un triaje KAPE del equipo, con datos en vivo y una copia del sistema de ficheros.

## Evidencias

- `TriageData/`: EVTX, `$MFT`, hives y perfil de Chrome.
- `LiveResponse/`: procesos, puertos, salida de CrowdResponse y `config.7z` con SAM/SYSTEM.
- Unos 3.104 ficheros en total.

```bash
sha256sum -c hashes.txt 2>/dev/null; ls TriageData LiveResponse
```

## Investigación

### 1. Inventario y triaje

El volumen obliga a elegir: `$MFT` para objetos, Security para logons y Sysmon para ejecución. Chainsaw permite filtrar sin abrir 3.000 ficheros uno a uno:

```bash
chainsaw hunt TriageData -s sigma/rules --mapping mappings/sigma-event-logs-all.yml \
  --csv out --output chainsaw.csv
EvtxECmd.exe -d TriageData/Windows/System32/winevt/Logs --csv out --csvf evtx.csv
```

### 2. Línea temporal

Security muestra un **4624 Logon Type 3** (red) de `Velma` desde `192.168.157.151` a las **17:15:56**: acceso a un recurso compartido desde otra máquina de la red interna, no un inicio de sesión interactivo.

Dos minutos después, Sysmon **EID 1** registra `cmd.exe` a las **17:17:43** y, en la misma sesión, `net group` y `net users`: enumeración de cuentas y grupos después de entrar.

El share está en el registro:

```text
HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Shares
```

Ahí se ve el recurso legítimo de ingeniería y su ruta.

### 3. Artefacto clave

En `Documents` hay un `bk_db.ibd` (copia de una base MySQL) con credenciales en texto claro: el atacante no necesitó cracking, solo abrir el fichero. Los hives de `config.7z` permiten confirmar la reutilización:

```bash
impacket-secretsdump -sam SAM -system SYSTEM LOCAL
```

El hash NTLM local coincide con la contraseña encontrada en el backup: la misma clave se usaba en la base y en la cuenta local.

El `$MFT` cierra el caso: `learn.txt` fue **creado por el atacante** en su perfil, no por el empleado, y contiene la contraseña usada para el acceso. La creación, no la modificación, es lo que prueba la autoría.

## Conclusiones

- Acceso por SMB con credenciales válidas de `Velma` desde una máquina interna, seguido de enumeración con `net group`/`net users`.
- La contraseña salió de un backup de base de datos en texto claro en el perfil del sospechoso y estaba reutilizada en la cuenta local.
- Fuga de propiedad intelectual mediante copia local; el `learn.txt` creado por el atacante es la evidencia de autoría.

## Lecciones

- Un `Logon Type 3` con nombre de usuario concreto descarta el anónimo: hay credencial, y hay que buscarla.
- Los backups de bases de datos (`*.ibd`, `.sql`, `.bak`) no se cifran casi nunca y contienen credenciales.
- La reutilización de contraseña convierte una filtración de backup en acceso al host.
- `$MFT` distingue creación de modificación; para autoría, la fecha de creación manda.

## Mitigaciones y detección

- Cifrar backups de bases de datos y no dejarlos en perfiles de usuario.
- Contraseñas únicas por servicio; gestor corporativo y rotación tras incidente.
- Monitorizar accesos 5140/5145 a shares sensibles y la enumeración posterior (`net group`, `net users` → Sysmon 1 con esas líneas).
- Retención de Sysmon y Security suficiente para reconstruir dos minutos de actividad.

MITRE: T1021.002 (SMB/admin shares), T1087.002 (domain account discovery), T1552.001 (credentials in files), T1005 (data from local system), T1078 (valid accounts).

## Referencias

- <https://mwalkowski.com/post/sherlock-jinkies>
- <https://inksec.io/blue-team/sherlocks/jinkies>
- <https://github.com/WithSecureLabs/chainsaw>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-5140>
