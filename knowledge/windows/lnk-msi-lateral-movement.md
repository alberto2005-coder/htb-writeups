---
topic: Windows — LNK envenenado y MSI firmado con una CA filtrada
tags: [windows, lnk, msi, code-signing, ca, lateral-movement, privesc]
---

# Windows — LNK envenenado y MSI firmado con una CA filtrada

[🌐 English](lnk-msi-lateral-movement.en.md) | **Español**

## Concepto

Un acceso directo escribible que otro usuario ejecuta se puede reemplazar por un LNK que lanza una shell. Si además se filtra la clave privada de una CA de firma de código y existe un directorio de MSIs que un administrador ejecuta, se puede firmar un MSI malicioso y obtener ejecución como ese administrador.

## Cuándo aplica

- Un LNK en una ruta pública es escribible.
- Otro usuario lo abre de forma periódica o al iniciar sesión.
- Hay una CA privada accesible y un directorio de despliegue de MSI.

## Procedimiento

1. Analizar el LNK con `pylnker` o `LECmd`.
2. Generar un LNK con `LNKUp` que ejecute la carga.
3. Reemplazar el archivo y esperar la ejecución.
4. Firmar un MSI con la CA filtrada y dejarlo en el directorio vigilado.

## Comandos

```bash
python LNKUp/generate.py --host localhost --type ntlm --out evil.lnk --execute 'cmd /c ...'
makecert -pe -n "CN=My SPC" -cy end -sky signature -ic MyCA.cer -iv MyCA.pvk -sv MySPC.pvk MySPC.cer
signtool sign /f MySPC.pfx /fd sha256 payload.msi
```

## Variantes

- LNK con `powershell`, `mshta` o doble OpenSSL.
- MSI con acción personalizada.
- Tarea programada que ejecuta el MSI.

## Limitaciones

- El LNK puede ser reemplazado por el script tras ejecutarse.
- El usuario puede no tener permisos de escritura.
- La CA puede no estar en el almacén de confianza.

## Mitigación

- Restringir escritura en accesos directos públicos.
- Proteger la clave privada de la CA y rotarla.
- Verificar el origen y la firma de los MSI.
- Auditar directorios de despliegue.

## Detección

- Cambios en LNK de rutas públicas.
- MSIs nuevos en directorios vigilados.
- `msiexec` ejecutando binarios fuera del catálogo.

## Referencias

- [0xdf — Ethereal](https://0xdf.gitlab.io/2019/03/09/htb-ethereal.html)
- [Microsoft — signtool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool)
- [MITRE — T1204.002](https://attack.mitre.org/techniques/T1204/002/)
