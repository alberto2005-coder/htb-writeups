---
sherlock: Heartbreaker-Continuum
domain: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, powershell, pe, packer, sftp, exfiltration]
---

# Heartbreaker-Continuum — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Una campaña de phishing romántico entrega un ejecutable disfrazado de imagen TIFF. El usuario lo abre y el programa muestra una foto mientras, por detrás, recopila documentos y los envía por SFTP. La evidencia es un único binario; hay que extraer la lógica y las credenciales que usa.

## Evidencias

```text
Heartbreaker-Continuum/Superstar_MemberCard.tiff.exe      binario entregado por correo
```

```bash
sha256sum Superstar_MemberCard.tiff.exe
file Superstar_MemberCard.tiff.exe
```

## Investigación

### 1. Inventario y triaje

Un solo PE de 32 bits. Se empieza por lo estático: `file`, `pefile`/PEStudio para cabeceras, secciones y timestamp; después `strings` en ASCII y UTF-16. El nombre con doble extensión ya dice que la imagen es señuelo.

```bash
python3 -c "import pefile;pe=pefile.PE('Superstar_MemberCard.tiff.exe');print(hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint), pe.FILE_HEADER.TimeDateStamp)"
strings -n 6 Superstar_MemberCard.tiff.exe | head -40
strings -el Superstar_MemberCard.tiff.exe | grep -iE 'http|sftp|password|powershell' | head
```

### 2. Línea temporal

El `TimeDateStamp` del PE y el de compilación del script embebido son coherentes con la campaña. No hay artefactos de ejecución en el paquete, así que la línea temporal se reconstruye desde el propio binario: se ejecuta, muestra la imagen, enumera el perfil y copia ficheros.

### 3. Artefacto clave

El binario es un **script de PowerShell compilado**: contiene una cadena en base64 invertida que, al decodificarla, revela el script. Ahí están las rutas que copia (`Documentos`, PDF, correo), la carpeta de staging `C:\Users\Public\HelpDesk-Tools`, la descarga de un WinSCP portable y las credenciales del servidor SFTP.

```bash
# extraer el blob y decodificar: invertir la cadena y luego base64
python3 - <<'PY'
import base64
blob = open('blob.b64','rb').read().strip()
print(base64.b64decode(blob[::-1]).decode('utf-16-le', 'replace'))
PY
```

## Conclusiones

- Entrega: phishing con excusa romántica y ejecutable con doble extensión `.tiff.exe`.
- Ejecución: PowerShell compilado que muestra un señuelo y trabaja en segundo plano.
- Acción: recolección de documentos y correo, compresión y exfiltración por SFTP con WinSCP portable.
- IOC: hash del binario, carpeta `HelpDesk-Tools`, nombre del servidor SFTP y la cuenta usada.
- Persistencia: no documentada en el binario.

## Lecciones

- Un `.exe` con nombre de imagen no es una imagen: la extensión doble sigue funcionando.
- "PowerShell compilado" no es un binario nativo: el script está dentro y se recupera invirtiendo y decodificando.
- Las credenciales de exfiltración suelen estar en el propio malware; extraerlas permite buscar el destino en el proxy.
- Mitigación: bloquear ejecutables desde carpetas de usuario, quitar la asociación de dobles extensiones y aplicar ASR.
- Detección: `4688` con `powershell.exe` desde `%TEMP%`, creación de `C:\Users\Public\HelpDesk-Tools`, ejecución de `WinSCP.exe` portable y conexiones SFTP salientes.
- Lo que faltaría: captura de red o logs de proxy para confirmar la subida.

MITRE: T1204.002 (malicious file), T1059.001 (PowerShell), T1074.001 (local data staging), T1048.002 (exfiltration over asymmetric encrypted channel).
