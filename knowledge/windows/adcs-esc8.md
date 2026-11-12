# AD CS ESC8 — NTLM Relay contra Web Enrollment

[🇬🇧 English](adcs-esc8.en.md) | **Español**

## Resumen

ESC8 es una condición de abuso de Active Directory Certificate Services (AD CS) en la que un endpoint HTTP de Certificate Authority Web Enrollment (o un servicio web de inscripción equivalente) acepta autenticación NTLM y puede ser alcanzado mediante un ataque de relay. En vez de conocer la contraseña o recuperar el hash NTLM de la víctima, el atacante induce una autenticación NTLM hacia un endpoint controlado y retransmite el intercambio a la interfaz vulnerable.

El impacto depende de los permisos de inscripción, las plantillas disponibles y la identidad cuya autenticación se retransmite. En un entorno de dominio, una autenticación de una cuenta privilegiada puede permitir solicitar un certificado que habilite autenticación como esa cuenta.

> Realizar estas pruebas únicamente en laboratorios propios o entornos para los que exista autorización explícita.

## Requisitos y condiciones

- AD CS desplegado y un endpoint HTTP de Web Enrollment accesible.
- El endpoint acepta NTLM y no aplica protecciones eficaces contra relay.
- La víctima puede ser inducida a autenticarse contra un destino controlado por el operador de la prueba.
- La CA y las plantillas permiten emitir un certificado adecuado para la identidad solicitada.
- La cuenta autenticada tiene permisos suficientes para solicitar el certificado.

La presencia de AD CS por sí sola no demuestra ESC8. Hay que comprobar el protocolo de autenticación, el transporte, las protecciones del endpoint y los permisos de inscripción.

## Flujo conceptual

1. Identificar la CA y los endpoints de inscripción publicados.
2. Verificar, dentro del alcance autorizado, si el endpoint acepta NTLM sobre HTTP y qué protecciones aplica.
3. Determinar qué identidad podría autenticarse y qué plantillas puede solicitar.
4. Evaluar si el flujo de autenticación puede retransmitirse al servicio de inscripción.
5. Si la emisión es posible, validar el certificado y su uso de autenticación en el laboratorio.
6. Documentar la identidad afectada, permisos, plantilla, CA, evidencia y controles ausentes.

## Enumeración y revisión

Fuentes y herramientas habituales para inventario y auditoría:

- `certutil -config - -ping` para localizar/responder contra CAs conocidas.
- Certipy (por ejemplo, `certipy find`) para inventariar CAs, plantillas y configuraciones AD CS.
- BloodHound/SharpHound y consultas LDAP para contextualizar grupos, ACL y permisos.
- Revisión de IIS, bindings, autenticación Windows, NTLM y Extended Protection for Authentication (EPA).

La enumeración debe registrar, como mínimo:

- FQDN y rutas de los endpoints web.
- HTTP frente a HTTPS y configuración TLS.
- Métodos de autenticación habilitados.
- Estado de EPA/channel binding y requisitos de firma.
- Plantillas publicadas, EKU, enrolment rights y aprobación/firmas requeridas.
- Cuenta de servicio y permisos sobre la CA.

## Mitigación

- Deshabilitar NTLM en los endpoints de inscripción cuando sea viable y migrar a Kerberos.
- Exigir HTTPS y configurar Extended Protection for Authentication (EPA) correctamente.
- Aplicar channel binding y protecciones contra NTLM relay en IIS/servicios compatibles.
- Restringir o deshabilitar Web Enrollment si no es necesario.
- Limitar quién puede inscribirse en plantillas sensibles; revisar EKU, subject/SAN supply y aprobación.
- Reducir exposición de HTTP y segmentar los servidores AD CS.
- Auditar y monitorizar solicitudes de certificados, especialmente solicitudes inesperadas para cuentas privilegiadas.
- Aplicar las recomendaciones vigentes de Microsoft para AD CS, IIS y NTLM.

HTTPS por sí solo no garantiza protección contra relay: deben revisarse EPA/channel binding y el comportamiento de autenticación del servicio.

## Detección y respuesta

- Correlacionar eventos de emisión de certificados de la CA (por ejemplo, eventos de auditoría de AD CS disponibles en la configuración del entorno).
- Buscar solicitudes inusuales, plantillas sensibles, solicitantes inesperados y SAN/UPN no habituales.
- Revisar logs IIS para rutas de inscripción, autenticación NTLM y patrones anómalos.
- Investigar autenticaciones de cuentas privilegiadas desde hosts inesperados.
- Ante sospecha, identificar y revocar certificados emitidos indebidamente, evaluar sesiones derivadas y rotar credenciales si procede.

## Diferencias con otros conceptos

- **NTLM relay** es la técnica general de retransmitir autenticación NTLM a otro servicio.
- **ESC8** es un escenario concreto de AD CS en el que un endpoint web de inscripción puede ser el destino del relay.
- **ESC1** trata de plantillas que permiten al solicitante especificar una identidad en el certificado; no es lo mismo que ESC8.
- **Shadow Credentials** modifica material de autenticación asociado a una cuenta; no es el mismo mecanismo que solicitar un certificado mediante Web Enrollment.

## Checklist de auditoría

- [ ] ¿Hay Web Enrollment u otro endpoint HTTP de inscripción?
- [ ] ¿Acepta NTLM?
- [ ] ¿Está forzado HTTPS?
- [ ] ¿EPA/channel binding está habilitado y validado?
- [ ] ¿Se puede deshabilitar NTLM en ese servicio?
- [ ] ¿Qué plantillas y permisos de inscripción están disponibles?
- [ ] ¿Se auditan y revisan las emisiones?
- [ ] ¿Existe un procedimiento de revocación y respuesta?

## Referencias

- Microsoft Learn — Certificate Authority Web Enrollment: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-authority-web-enrollment
- Microsoft Learn — Extended Protection for Authentication: https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/extended-protection-for-authentication-overview
- SpecterOps — Certified Pre-Owned: https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf
- Certipy: https://github.com/ly4k/Certipy
