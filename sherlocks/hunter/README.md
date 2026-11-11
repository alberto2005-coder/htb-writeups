---
sherlock: Hunter
domain: Threat Hunting
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [threat-hunting, dfir, windows, evtx, amcache, prefetch, keepass]
---

# Hunter — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un analista del SOC recibe una alerta de posible movimiento lateral y *credential stuffing*. La confianza es baja porque el SOC acaba de desplegarse, pero el análisis de red confirma el ataque. Se entrega el triaje del endpoint comprometido y una captura de red **incompleta**: el sensor tuvo problemas de rendimiento. El objetivo es reconstruir la intrusión completa, desde el acceso inicial hasta la exfiltración.

## Evidencias

- Triaje del endpoint (imagen de disco parcial), con `Windows\System32\winevt\logs\System.evtx` y `Security.evtx`.
- `Windows\AppCompat\Programs\Amcache.hve`.
- `Prefetch\*.pf`, incluido `WHOAMI.EXE-*.pf` y `CERTUTIL.EXE-*.pf`.
- `ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb` (índice de búsqueda de Windows).
- Perfil `C:\Users\alonzo.spire\`: Chrome (`User Data\Default`), Edge (`WebCache\WebCacheV01.dat`), `PSReadLine`, `FileZilla`, `NTUser.dat` y `UsrClass.dat`.
- Captura PCAP parcial, con tráfico FTP hacia la infraestructura del atacante.

```bash
sha256sum *.zip *.pcap     # anotar hashes antes de analizar
```

## Investigación

### 1. Inventario y triaje

Se empieza por la línea temporal barata: servicios, inicios de sesión y ejecución.

```bash
EvtxECmd.exe -f System.evtx --csv . --csvf system
EvtxECmd.exe -f Security.evtx --csv . --csvf security
PECmd.exe -d Prefetch --csv . --csvf prefetch
AmcacheParser.exe -f Amcache.hve --csv . --csvf amcache
```

- `System.evtx` muestra un **7045** (servicio creado): nombre aleatorio y binario `owUjOMCY.exe` en una ruta de usuario.
- `Security.evtx` muestra un **4624 tipo 3** (red) con la cuenta `alonzo.spire` justo después del 7045.
- `PECmd` fecha la ejecución de `whoami.exe` y `certutil.exe`; `AmcacheParser` da el SHA1 del ejecutable del servicio.

### 2. Línea temporal

La zona horaria es la trampa: las preguntas piden UTC y los EVTX pueden estar en hora local del host. Se normaliza todo a UTC antes de correlacionar.

1. Creación del servicio y arranque de `owUjOMCY.exe` (2023-06-21, por la mañana).
2. Logon de red de `alonzo.spire` (4624 tipo 3) y `whoami` inmediato.
3. `certutil` descarga `scout.bat` desde el C2 y lo ejecuta.
4. Acceso RDP del atacante con credenciales de administrador (4624 tipo 10).
5. Enumeración con PowerShell y volcado de KeePass.
6. Exfiltración por FTP y, al fallar, por una instancia en la nube.

### 3. Artefacto clave

**Credenciales del PDF sin el PDF.** El índice de búsqueda de Windows guarda contenido y metadatos de documentos que ya no están. `SIDR` (Search Index DB Reporter) sobre `Windows.edb` recupera el texto indexado de `Internal_Documentation.pdf`, incluidas las credenciales RDP del administrador.

```bash
SIDR.exe -f Windows.edb -o sidr.csv
```

**El resto de la cadena** se apoya en artefactos de usuario:

- `PSReadLine\ConsoleHost_history.txt`: el atacante ejecuta `clean.ps1`; los cmdlets que contiene (`Get-NetDomainController`) delatan que es PowerView renombrado.
- Chrome `History`: descargas de FileZilla, KeePass y Process Hacker; el jumplist muestra el volcado `pid9180.dmp` de KeePass.
- `CryptnetUrlCache\MetaData` y `\Content`: `certutil` deja la URL del C2 y el propio `scout.bat`, cuyo MD5 se calcula sobre el fichero recuperado.
- `FileZilla\filezilla.xml` y `recentservers.xml`: host, usuario, contraseña y ruta remota del FTP.
- `NTUser.dat` → `UserAssist`: tiempo de uso de FileZilla (10 min 48 s = 648 s).
- `UsrClass.dat` → shellbags: directorio `Documents` con el ZIP del proyecto sensible.
- PCAP: el FTP transporta `Keepassproc.zip` y `database.kdbx`; el ZIP va cifrado con la misma contraseña del FTP.

**Del volcado al contenido.** El dump de KeePass se ataca con la vulnerabilidad **CVE-2023-32784** (recuperación del *master password* desde memoria) y `keepass-password-dumper`. Con la clave se abre `database.kdbx`, se obtienen las credenciales del ZIP del proyecto y dentro aparece la nota con el nombre de la aplicación interna y el JSON con los SSN.

## Conclusiones

- Acceso inicial por **servicio Windows** (T1569.002) con un binario de nombre aleatorio; el 7045 y el 4624 tipo 3 lo prueban.
- Reconocimiento con PowerView renombrado, herramientas descargadas por el navegador y `certutil` como *download cradle*.
- Escalada de privilegios por **credenciales en un PDF indexado** y posterior RDP como administrador.
- Exfiltración por FTP con FileZilla; al fallar, una instancia en la nube del atacante.
- Robo de la base KeePass y abuso de CVE-2023-32784 para abrir el proyecto y los datos personales.
- IOCs principales: nombre del servicio y del ejecutable, URL del C2, hash de `scout.bat`, host y ruta del FTP. Los valores concretos quedan en `private/`.

## Lecciones

- **El índice de búsqueda es evidencia**: `Windows.edb` conserva texto de documentos borrados; sin él, el PDF sería irrecuperable.
- **`CryptnetUrlCache` y Prefetch**: la pareja `certutil.exe` + caché de URL da la descarga y el contenido, aunque el fichero ya no esté.
- **UserAssist y shellbags**: cuantifican uso y directorios visitados sin necesidad de memoria.
- **KeePass en memoria**: un dump de proceso más CVE-2023-32784 equivale a la contraseña maestra; deshabilitar volcados de procesos y proteger el portátil.
- **Captura parcial**: con solo una parte del PCAP, los artefactos del endpoint sostienen la reconstrucción. La organización debería revisar la retención y el dimensionado del sensor.
