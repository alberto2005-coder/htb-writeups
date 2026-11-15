---
topic: Electron — actualizaciones y firma de paquetes
tags: [windows, electron, updater, smb, code-signing]
---

# Electron — actualizaciones y firma de paquetes

[🌐 English](electron-updater-signature-bypass.en.md) | **Español**

## Concepto

Las aplicaciones Electron suelen actualizarse con `electron-updater` leyendo un manifiesto `latest.yml` y descargando un paquete. Si el recurso de actualizaciones es escribible y el cliente no valida la firma del publicador, un atacante reemplaza el manifiesto y el binario para ejecutar código en la siguiente comprobación.

## Cuándo aplica

- Un recurso SMB o HTTP de actualizaciones permite escritura.
- La app usa `electron-updater` o un actualizador propio sin firma.
- El usuario abre la aplicación o esta comprueba actualizaciones al iniciar.

## Procedimiento

1. Localizar el manifiesto y el recurso de actualizaciones.
2. Crear un paquete con el mismo nombre y versión superior.
3. Sustituir `latest.yml` y el binario.
4. Esperar la comprobación y verificar la ejecución.

## Comandos

```bash
smbclient -N //<IP>/Software_Updates
# latest.yml apunta al paquete malicioso
cat latest.yml
# Publicar el payload y el manifiesto
smbclient -N //<IP>/Software_Updates -c "put latest.yml; put payload.exe"
```

## Variantes

- Aprovechar una ruta de actualización HTTP sin TLS.
- Firmar con un certificado robado o autofirmado si el cliente no comprueba la cadena.
- Usar un canal de actualización de un plugin o de la app móvil.

## Limitaciones

- El cliente puede validar la firma Authenticode.
- El recurso debe ser escribible por el atacante.
- La versión debe ser superior a la instalada.

## Mitigación

- Firmar los paquetes y validar la firma en el cliente.
- Servir actualizaciones por TLS con allowlist.
- Restringir la escritura en el recurso y monitorizar cambios en `latest.yml`.

## Detección

- Cambios en `latest.yml` fuera de un despliegue.
- Paquetes descargados desde rutas no habituales.
- Procesos hijos del actualizador ejecutando binarios nuevos.

## Referencias

- [0xdf — Atom](https://0xdf.gitlab.io/2021/07/10/htb-atom.html)
- [Electron — autoUpdater](https://www.electronjs.org/docs/latest/api/auto-updater)
- [CWE-494 — Download of Code Without Integrity Check](https://cwe.mitre.org/data/definitions/494.html)
