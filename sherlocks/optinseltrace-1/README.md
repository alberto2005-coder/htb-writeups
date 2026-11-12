---
sherlock: OpTinselTrace-1
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, insider, em-client, jumplists, mft]
---

# OpTinselTrace-1 — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales.

## Escenario

“Elfin” trabaja en horarios extraños y parece saltarse controles. La inteligencia de Santa sospecha un insider. Se entrega un triaje KAPE de su estación y una captura de respuesta en vivo; hay que auditar la actividad del usuario, su correo y los archivos que pudo enviar.

## Evidencias

- `TriageData`: `$MFT`, USN Journal, registro, EVTX, perfiles y artefactos de aplicaciones.
- `LiveResponse`: procesos, conexiones y captura del sistema en el momento de la recolección.
- Cliente de correo `eM Client` en `AppData\Roaming`.
- Listas de salto, `RecentDocs` y MFT/USN.

```bash
sha256sum optinseltrace-1.zip
unzip -l optinseltrace-1.zip | head -30
```

## Investigación

### 1. Inventario y triaje

La captura en vivo permite identificar el cliente de correo y su proceso:

```text
LiveResponse/pstree.txt
LiveResponse/netstat.txt
TriageData/Users/<USER>/AppData/Roaming/eM Client
```

`pstree` muestra `MailClient.exe` bajo `explorer.exe`, lo que confirma que el usuario lo abrió. La carpeta de `eM Client` contiene cuentas, carpetas y adjuntos.

### 2. Línea temporal

Se cruzan:

- Apertura de `eM Client` y última actividad.
- Correos enviados/recibidos y adjuntos.
- Creación del binario y del ZIP en el disco.
- Listas de salto y `RecentDocs` para la ruta exacta.
- USN/MFT para la hora de creación.

```bash
MFTECmd.exe -f '$MFT' --csv mft.csv
JLECmd.exe -d AutomaticDestinations --csv jl.csv
```

### 3. Artefacto clave

El correo enviado contiene un binario comprimido (`santa_deliveries.zip`) con credenciales hardcodeadas y lógica para consultar un bucket S3. La lista de salto y el MFT dan la hora de creación y la carpeta desde la que se preparó. El binario se analiza con `strings` y un descompilador.

```text
eM Client -> correo -> adjunto ZIP -> binario -> credenciales/S3
```

## Conclusiones

- Elfin usó su cliente de correo para enviar un binario sensible a un tercero.
- El ZIP se creó en una carpeta del perfil y se adjuntó al correo.
- El binario contiene credenciales y acceso a un bucket S3.
- Los IOCs son la cuenta de correo, el nombre del ZIP, el hash del binario y el bucket.

## Lecciones

- `eM Client` guarda cuentas y mensajes en `AppData\Roaming`.
- Las listas de salto aportan la ruta y el momento de creación.
- El MFT/USN confirma la secuencia aunque el correo se borre.
- Un insider puede exfiltrar sin malware; el correo es el canal.

## Referencias

- <https://writeups.chicken0248.fyi/HackTheBox/HTB%20Labs/HTB%20Sherlocks/%5BHTB%20Sherlocks%20Write-up%5D%20OpTinselTrace-1>
- <https://www.emclient.com/>
- <https://attack.mitre.org/techniques/T1567/002/>
