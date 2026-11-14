---
machine: Ypuffy
os: OpenBSD
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [openbsd, ldap, samba, ssh-ca, doas]
---

# Ypuffy — Hack The Box (OpenBSD)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

LDAP permite bind anónimo y expone el hash Samba de `alice1978`. Con pass-the-hash se accede a su share SMB y se descarga una clave PuTTY. `alice1978` puede ejecutar `ssh-keygen` como `userca` con `doas`; la CA de `userca` firma una clave con principal de root y permite SSH como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh     OpenSSH 7.7
80/tcp   http    OpenBSD httpd
139/tcp  netbios-ssn Samba
389/tcp  ldap    Anonymous bind OK
445/tcp  microsoft-ds Samba 4.7.6
```

## Enumeración

- `ldapsearch -x -b dc=hackthebox,dc=htb` devuelve usuarios y atributos Samba.
- `alice1978` tiene `sambaNTPassword`; `bob8791` aparece como segunda cuenta.
- El share `alice` contiene `my_private_key.ppk`.
- La web solo expone `/userca` y `/sshauth`; el resto se bloquea.

## Foothold

Se usa el hash NTLM con `smbclient` o `impacket` para autenticarse como `alice1978` sin conocer la contraseña. Del share se descarga la clave `.ppk`, que se convierte a formato OpenSSH con `puttygen`.

```bash
smbclient //<IP>/alice -U alice1978 --pw-nt-hash <NTLM_HASH>
puttygen my_private_key.ppk -O private-openssh -o alice.key
ssh -i alice.key alice1978@<IP>
```

## Movimiento lateral

`/etc/doas.conf` permite a `alice1978` ejecutar `/usr/bin/ssh-keygen` como `userca` sin contraseña. En `/home/userca` están `ca` y `ca.pub`, la CA que firma las claves aceptadas por `sshd`.

`sshd_config` usa `TrustedUserCAKeys` y `AuthorizedPrincipalsCommand`; un certificado con el principal adecuado se acepta como root.

## Escalada de privilegios

Se genera un par de claves, se firma la pública con la CA de `userca` y se establece el principal de root. El certificado resultante se presenta a `sshd`.

```bash
doas -u userca ssh-keygen -s /home/userca/ca -I <ID> -n root -V +1d alice.key.pub
ssh -i alice.key root@<IP>
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales, si existen, viven en `private/` y no se publican.

## Lecciones aprendidas

- Un LDAP anónimo puede filtrar hashes de Samba.
- El pass-the-hash evita la necesidad de crackear.
- Una CA de SSH accesible con `doas` es equivalente a root si acepta cualquier principal.
- Los certificados de corta duración no compensan una CA mal protegida.

## Mitigaciones y detección

- Requerir autenticación LDAP y limitar atributos legibles.
- Deshabilitar NTLM y usar Kerberos o credenciales modernas.
- Restringir `ssh-keygen` por principal y comando; proteger la CA.
- Auditar `TrustedUserCAKeys` y los principales permitidos.

## Referencias

- [0xdf — Ypuffy](https://0xdf.gitlab.io/2019/02/09/htb-ypuffy.html)
- [AnubisSec — Ypuffy](https://anubissec.github.io/Ypuffy-Hackthebox-WriteUp/)
- [Búsqueda de vídeos (CSV)](https://www.youtube.com/results?search_query=ippsec+ypuffy)
