---
sherlock: Malevolent ModMaker
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, go, ransomware, discord-webhook, aes-gcm, powershell, reverse-engineering]
---

# Malevolent ModMaker — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un ingeniero de Acme descarga una herramienta para crear mods de un videojuego desde una comunidad. La ejecuta como administrador y sus archivos desaparecen. Se entregan varios ejecutables, una nota y un archivo cifrado para reconstruir la cadena y recuperar el contenido.

## Evidencias

- `MCModMaker-v.1.4.exe`, el señuelo.
- `goteem.exe`, el binario de segunda etapa.
- Nota de rescate y archivo con extensión anómala.
- Los ejecutables se analizan sin ejecutarlos.

```bash
sha256sum * 2>/dev/null
file *
```

## Investigación

### 1. Inventario y triaje

Se identifican los PE y se calculan hashes antes de abrirlos. La nota y la extensión del archivo cifrado apuntan a ransomware. `strings` y un descompilador de Go muestran que `goteem.exe` es la segunda etapa.

- `MCModMaker-v.1.4.exe` es el dropper.
- `goteem.exe` es un binario Go de ransomware.
- El archivo `.txt` con extensión extraña es el dato cifrado.

### 2. Comportamiento del dropper

El señuelo ejecuta comandos de reconocimiento (`whoami`, `hostname`, `ipconfig`, `dir`), consulta un servicio de geolocalización y envía los datos a un webhook de Discord. Después descarga `goteem.exe` y lo ejecuta con PowerShell usando `-ep -bypass`.

```text
whoami → hostname → ipconfig → dir → geolocalización → webhook → PowerShell → goteem.exe
```

El uso de un webhook de chat como C2 evita dominios dedicados y mezcla el tráfico con servicios legítimos.

### 3. Ransomware y cifrado

`goteem.exe` recorre el sistema de archivos, omite directorios sin permisos y cifra archivos de texto con AES-GCM. La clave está embebida en el binario, por lo que se puede recuperar con análisis estático.

```text
clave AES-GCM embebida → nonce + ciphertext + tag → descifrado sin ejecutar el malware
```

## Conclusiones

- El acceso inicial fue ingeniería social en una comunidad de gaming.
- El dropper perfiló el host y usó Discord como canal encubierto.
- La segunda etapa es un ransomware Go con clave simétrica embebida.
- La recuperación es posible sin pagar porque la clave está en el binario.

## Lecciones

- Los ejecutables compartidos en comunidades no son confiables.
- Los webhooks de Discord son un canal C2 difícil de bloquear por dominio.
- Una clave embebida en ransomware permite recuperación estática.
- El análisis debe preservar hashes y cadena de custodia.

## Referencias

- <https://www.hackthebox.com/sherlocks/Malevolent%20ModMaker>
- <https://attack.mitre.org/techniques/T1204/002/>
- <https://attack.mitre.org/techniques/T1102/001/>
- <https://attack.mitre.org/techniques/T1486/>
