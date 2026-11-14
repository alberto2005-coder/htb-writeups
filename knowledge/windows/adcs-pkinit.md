---
topic: ADCS, PKINIT y plantillas vulnerables
tags: [windows, active-directory, adcs, pkinit, certificates, esc1]
---

# ADCS, PKINIT y plantillas vulnerables

[🇬🇧 English](adcs-pkinit.en.md) | **Español**

## Concepto

Active Directory Certificate Services emite certificados para autenticación. Una plantilla que permite al solicitante especificar el sujeto y un EKU de smart card puede convertirse en un certificado de cualquier usuario. PKINIT usa ese certificado para obtener un TGT.

## Cuándo aplica

- ADCS instalado y plantillas publicadas.
- Permisos de inscripción para un usuario de dominio.
- Plantilla con `ENROLLEE_SUPPLIES_SUBJECT` y EKU de autenticación.

## Procedimiento

1. Enumerar CA y plantillas.
2. Buscar plantillas con sujeto controlable y EKU adecuado.
3. Solicitar el certificado con el `upn` del objetivo.
4. Convertir el PFX a formato PKINIT.
5. Obtener el TGT y usarlo.

```bash
certipy-ad find -u <USER>@<DOMAIN> -p <PASS> -dc-ip <DC>
certipy-ad req -u <USER>@<DOMAIN> -p <PASS> -ca <CA> -template <TEMPLATE> -upn administrator@<DOMAIN>
```

## Variantes

- ESC1 (sujeto controlable).
- ESC2/ESC3 (EKU y agentes de inscripción).
- ESC8 (relay HTTP a ADCS).

## Limitaciones

- La plantilla debe permitir la inscripción.
- El EKU debe servir para autenticación.
- Los parches y la auditoría pueden bloquear ESC1.

## Mitigación

- Revisar permisos y EKU de las plantillas.
- Deshabilitar `ENROLLEE_SUPPLIES_SUBJECT` salvo necesidad.
- Requerir aprobación y auditar emisiones.
- Proteger el tráfico de inscripción.

## Detección

- Solicitudes con `upn` de otro usuario.
- Emisiones fuera de horario.
- Autenticaciones PKINIT inusuales.

## Referencias

- <https://posts.specterops.io/certified-pre-owned-d95910965cd2>
- <https://github.com/ly4k/Certipy>
- <https://attack.mitre.org/techniques/T1649/>
