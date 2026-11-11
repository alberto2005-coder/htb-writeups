# PassTheCert

## Resumen

PassTheCert es una técnica de abuso de autenticación basada en certificados en Active Directory. Cuando se dispone de un certificado válido y su clave privada para una identidad, ciertos servicios de AD pueden aceptar autenticación mediante certificado (por ejemplo, TLS client authentication en LDAP/LDAPS). La técnica permite utilizar esa identidad para realizar operaciones autorizadas por sus permisos, sin necesitar su contraseña.

PassTheCert no es una vulnerabilidad única ni implica que cualquier certificado permita autenticarse contra cualquier servicio. El resultado depende del certificado, la asociación de identidad, la configuración del dominio, el servicio y las políticas de autenticación.

> Usar únicamente en dominios de laboratorio o evaluaciones autorizadas.

## Conceptos clave

- **Certificado:** contiene una clave pública y atributos/identificadores que pueden vincularse a una cuenta.
- **Clave privada:** permite demostrar posesión de la identidad criptográfica asociada.
- **Schannel / TLS client authentication:** mecanismo que algunos servicios Windows pueden usar para autenticar clientes mediante certificados.
- **LDAP/LDAPS:** puede aceptar autenticación basada en certificado si el controlador de dominio y el cliente están configurados para ello.
- **Permisos AD:** una autenticación válida no concede privilegios adicionales por sí misma; las operaciones posibles dependen de ACL y grupos de la cuenta.

## Requisitos

- Un certificado válido para el contexto de autenticación del dominio.
- Acceso a la clave privada correspondiente.
- Un servicio que admita y confíe en la autenticación por certificado.
- Una asociación válida entre el certificado y la cuenta, según la configuración y el método de mapeo vigente.
- Permisos suficientes en AD para la acción que se pretende validar.

## Flujo de evaluación

1. Identificar cómo se obtuvo el certificado y a qué identidad está asociado.
2. Verificar vigencia, cadena de confianza, EKU, SAN/UPN y disponibilidad de la clave privada.
3. Determinar si el servicio objetivo admite autenticación TLS con certificado.
4. Comprobar el método de mapeo de certificados aplicado por los controladores de dominio.
5. En un laboratorio, validar autenticación contra LDAP/LDAPS y confirmar la identidad resultante.
6. Evaluar únicamente operaciones permitidas por los privilegios de esa cuenta.
7. Documentar certificado, identidad, servicio, método de mapeo y permisos observados.

## Herramientas y contexto

- Certipy: inventario y evaluación de AD CS; algunas funciones dependen de la versión y del escenario.
- OpenSSL: inspección de certificados y claves en formatos compatibles.
- `certutil`: inspección y gestión de certificados en Windows.
- Herramientas LDAP: validación de conectividad, TLS y permisos de directorio.
- PassTheCert (proyecto/herramienta): consultar documentación y versión actual antes de usarla; los argumentos y capacidades pueden cambiar.

No se deben copiar comandos de una guía sin verificar versión, formato de certificado, método de mapeo y compatibilidad del servicio.

## Diferencias con técnicas relacionadas

- **Pass-the-Certificate / PassTheCert:** utiliza un certificado y su clave privada para autenticarse ante un servicio compatible.
- **PKINIT:** extensión de Kerberos que permite autenticación inicial basada en clave pública; no es idéntica a la autenticación TLS de LDAP.
- **Shadow Credentials:** modifica atributos de una cuenta para registrar material de clave pública usado en autenticación, a menudo asociado a PKINIT.
- **AD CS ESC8:** abusa de NTLM relay contra Web Enrollment para obtener un certificado; PassTheCert puede ser una fase posterior si el certificado obtenido permite autenticación.
- **Pass-the-Hash:** utiliza material NTLM, no un certificado X.509.

## Mitigación y hardening

- Proteger AD CS y las plantillas: limitar enrollment rights, EKU, subject/SAN supply y aprobación.
- Proteger las claves privadas; evitar exportabilidad innecesaria y aplicar controles de acceso fuertes.
- Mantener una PKI confiable y retirar certificados comprometidos o innecesarios.
- Revisar y endurecer el mapeo de certificados a cuentas conforme a la guía vigente de Microsoft, especialmente tras cambios de seguridad de certificate-based authentication.
- Aplicar actualizaciones de Windows y configurar los modos de enforcement recomendados.
- Auditar autenticaciones basadas en certificado y cambios en atributos de mapeo.
- Reducir privilegios y revisar ACL de objetos sensibles en AD.

## Detección y respuesta

- Revisar eventos de autenticación de Kerberos/Schannel/LDAP disponibles en la versión y configuración del entorno.
- Investigar autenticaciones por certificado desde equipos o ubicaciones inusuales.
- Correlacionar el certificado (issuer, serial, thumbprint, SAN/UPN) con la cuenta autenticada.
- Revisar cambios recientes en atributos de mapeo de certificados y solicitudes/emisiones de AD CS.
- Si una clave privada está comprometida, revocar el certificado, localizar copias y evaluar el uso posterior de la identidad.

## Checklist

- [ ] ¿Cuál es el origen y propietario del certificado?
- [ ] ¿Se dispone de la clave privada y está protegida?
- [ ] ¿La cadena y el EKU son adecuados para el uso?
- [ ] ¿Qué método de mapeo de certificados está configurado?
- [ ] ¿El servicio acepta autenticación de cliente mediante certificado?
- [ ] ¿Qué permisos tiene la cuenta asociada?
- [ ] ¿Se auditan autenticaciones y cambios de mapeo?
- [ ] ¿Existe un proceso de revocación ante compromiso?

## Referencias

- Microsoft Learn — Certificate-based authentication: https://learn.microsoft.com/en-us/windows-server/security Kerberos (consultar la documentación vigente de certificate-based authentication y strong certificate mapping).
- Microsoft Learn — KB5014754, certificate-based authentication changes: https://support.microsoft.com/help/5014754
- PassTheCert: https://github.com/AlmondOffSec/PassTheCert
- Certipy: https://github.com/ly4k/Certipy
