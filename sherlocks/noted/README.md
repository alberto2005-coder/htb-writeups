---
sherlock: Noted
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, notepad++, extorsion, hands-on-keyboard, osint]
---

# Noted — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Simon, desarrollador de Forela, encuentra en su escritorio una nota de extorsión: alguien dice haber recogido datos de su equipo. El CERT sólo entrega los **artefactos de Notepad++** porque sospecha que el atacante redactó la nota y trabajó desde esa aplicación con acceso manual al teclado.

## Evidencias

```text
Noted/C/Users/Simon.stark/AppData/Roaming/Notepad++/
├── config.xml
├── session.xml
├── shortcuts.xml
└── backup/
    ├── LootAndPurge.java@2023-07-24_145332
    └── YOU HAVE BEEN HACKED.txt@2023-07-24_150548
```

## Investigación

### 1. Historial de ficheros

`config.xml` guarda la lista de recientes en objetos `<File filename="...">`. De ahí sale el script de operaciones con AWS de Simon y la ruta de su proyecto:

```bash
grep -o 'filename="[^"]*"' config.xml | sort -u
```

```text
C:\Users\Simon.stark\Documents\Dev_Ops\AWS_objects migration.pl
```

### 2. Copias de seguridad

`backup/` conserva el contenido de los documentos abiertos, incluso sin guardar. El nombre del fichero incluye la fecha y la hora del último guardado:

```bash
strings -n 6 "backup/YOU HAVE BEEN HACKED.txt@2023-07-24_150548" | head -40
```

La nota pide una cantidad en criptomoneda y deja un correo de contacto en la red Tor. `session.xml` fecha la última modificación del código Java en **2023-07-24 09:53:23 UTC** (timestamps NTFS en el XML), que es el momento en que el atacante compiló su herramienta.

### 3. El programa del atacante

`LootAndPurge.java` es código Java que recorre el perfil, selecciona documentos y los comprime en `Forela-Dev-Data.zip`, protegiéndolo con contraseña antes de sacarlo.

```bash
grep -nE "zip|password|File" "backup/LootAndPurge.java@2023-07-24_145332" | head -20
```

### 4. Contacto (OSINT)

El correo de la nota apunta a un proveedor de correo anónimo en `.onion`; el monedero es una dirección **ETH**. El reto pide localizar la dirección de soporte del proveedor, no interactuar con el atacante.

## Conclusiones

- No hay malware: el atacante trabajó **en la sesión de Simon** (hands-on-keyboard) y usó su propio IDE.
- Objetivo: código y planes de desarrollo; el script de AWS era el mapa.
- Prueba: los artefactos de Notepad++ dan ruta y hora de cada fichero.

## Lecciones

- Las aplicaciones de escritorio guardan más de lo que el usuario cree: recientes, backups y sesión.
- `session.xml` y `config.xml` se complementan: el primero dice qué estaba abierto, el segundo qué se abrió alguna vez.
- Un ZIP con contraseña generado en el host sigue siendo exfiltración; la contraseña viaja aparte.
- Mitigación: limpiar historiales sensibles, no guardar credenciales en scripts y usar gestor de secretos.
