# NTLM Relay

## Resumen

NTLM Relay es una técnica en la que un intermediario retransmite en tiempo real un intercambio de autenticación NTLM entre una víctima y un servicio de destino. El operador no necesita conocer la contraseña en texto claro ni romper el hash: aprovecha que el destino acepta la autenticación retransmitida y que faltan protecciones como firma SMB, LDAP signing/channel binding o Extended Protection for Authentication (EPA), según el protocolo.

No debe confundirse con **capturar y crackear hashes NTLM**. En relay, el intercambio se reenvía a otro servicio; no se obtiene necesariamente un hash reutilizable.

> Uso exclusivo en laboratorios y evaluaciones autorizadas.

## Componentes y condiciones

- Una identidad que inicia autenticación NTLM.
- Un servicio al que esa identidad se conecta o es inducida a conectarse.
- Un destino que acepta NTLM y no valida adecuadamente la integridad/canal de la conexión.
- Una acción permitida por los privilegios de la identidad autenticada.

Los destinos y el impacto varían: SMB, LDAP/LDAPS, HTTP, AD CS Web Enrollment y otros servicios compatibles. No todos los protocolos permiten las mismas acciones.

## Flujo conceptual

1. Identificar servicios que aceptan NTLM y comprobar las protecciones configuradas.
2. Identificar rutas legítimas o inducidas por las que una cuenta puede autenticarse.
3. Evaluar, en un laboratorio, si el intercambio puede retransmitirse al servicio de destino.
4. Determinar qué operaciones permite la identidad en ese servicio.
5. Validar el impacto con una acción inocua y documentar las condiciones.
6. Corregir la configuración y repetir la comprobación defensiva.

## Superficies habituales

| Destino | Controles relevantes | Riesgo si faltan |
|---|---|---|
| SMB | SMB signing, restricciones NTLM | Relay a servicios SMB vulnerables |
| LDAP | LDAP signing, channel binding, LDAPS bien configurado | Operaciones LDAP con la identidad retransmitida |
| HTTP/IIS | HTTPS, EPA, channel binding, autenticación | Relay a aplicaciones o Web Enrollment |
| AD CS Web Enrollment | NTLM, EPA, permisos y plantillas | Emisión de certificados (relacionado con ESC8) |

LDAPS o HTTPS no deben considerarse automáticamente inmunes: la protección depende de la validación de canal, EPA y la configuración concreta.

## Enumeración y auditoría

- Inventariar dónde se usa NTLM y dónde puede deshabilitarse.
- Revisar políticas de seguridad de dominio y directivas locales relacionadas con LAN Manager/NTLM.
- Comprobar SMB signing en clientes y servidores.
- Revisar LDAP signing y LDAP channel binding en controladores de dominio.
- Revisar IIS Windows Authentication y EPA en aplicaciones web.
- Usar herramientas de inventario como `ntlmrelayx` únicamente en laboratorios autorizados para validar controles, no para operar contra redes ajenas.
- Correlacionar autenticaciones NTLM con host de origen, cuenta, servicio y hora.

## Mitigación

- Reducir y, cuando sea viable, deshabilitar NTLM; migrar a Kerberos.
- Exigir SMB signing en servidores y clientes.
- Exigir LDAP signing y configurar LDAP channel binding según la compatibilidad del entorno.
- Configurar EPA en IIS y servicios compatibles.
- Usar HTTPS/LDAPS correctamente, con validación de certificados y channel binding.
- Restringir tráfico entre segmentos y limitar qué equipos pueden alcanzar servicios de autenticación.
- Deshabilitar servicios heredados innecesarios y evitar que cuentas privilegiadas inicien sesión en estaciones de trabajo no confiables.
- Aplicar políticas de Windows para restringir NTLM de forma gradual, monitorizando antes de bloquear.

## Detección

- Auditar eventos de NTLM en controladores de dominio y endpoints; revisar los registros disponibles según la versión de Windows y la política de auditoría.
- Correlacionar una misma cuenta autenticándose desde hosts inesperados o hacia múltiples servicios en intervalos anómalos.
- Buscar autenticaciones NTLM desde servidores que normalmente no actúan como clientes.
- Vigilar cambios LDAP sensibles, creación/modificación de objetos y solicitudes de certificados.
- No basar la detección en un único evento: correlacionar identidad, origen, destino, protocolo y operación.

## NTLM Relay frente a Pass-the-Hash

- **NTLM Relay:** retransmite un intercambio de autenticación activo a otro servicio.
- **Pass-the-Hash:** utiliza material de hash NTLM como credencial para autenticarse, cuando el protocolo y el entorno lo permiten.
- **Captura de NetNTLM:** obtiene un desafío/respuesta que podría intentarse crackear offline; no equivale a relay.

## Checklist defensivo

- [ ] ¿Dónde sigue habilitado NTLM?
- [ ] ¿SMB signing está requerido?
- [ ] ¿LDAP signing está requerido?
- [ ] ¿LDAP channel binding está configurado?
- [ ] ¿IIS y otros servicios web aplican EPA?
- [ ] ¿Las cuentas privilegiadas están protegidas frente a autenticaciones inducidas?
- [ ] ¿Se monitorizan autenticaciones NTLM y operaciones sensibles?
- [ ] ¿Existe un plan de reducción de NTLM probado por fases?

## Referencias

- Microsoft Learn — Restrict NTLM: https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-ntlm-authentication-in-this-domain
- Microsoft Learn — LDAP signing: https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server
- Microsoft Learn — SMB signing: https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing
- Impacket: https://github.com/fortra/impacket
- SpecterOps — Certified Pre-Owned: https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf
