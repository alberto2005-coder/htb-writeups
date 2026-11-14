---
topic: Excel XLL — add-in malicioso y ejecución
tags: [windows, phishing, xll, office, initial-access]
---

# Excel XLL — add-in malicioso y ejecución

[🌐 English](xll-phishing.en.md) | **Español**

## Concepto

Un XLL es una DLL que Excel carga como complemento. Aunque tiene icono de Excel, es un PE que ejecuta código nativo al habilitarse; una función exportada como `xlAutoOpen` se llama automáticamente. Fue un vector de phishing popular cuando las macros empezaron a bloquearse.

## Cuándo aplica

- La organización usa Excel y permite complementos de ubicaciones no confiables.
- El correo o un share entrega archivos con extensión `.xll`.
- Se busca ejecución en el escritorio de un usuario sin depender de macros VBA.

## Procedimiento

1. Crear un proyecto DLL con el SDK de Excel y exportar `xlAutoOpen`.
2. Compilar en Release para evitar dependencias de depuración.
3. Implementar una reverse shell o un cargador y enviar el XLL por correo o chat.
4. Esperar a que el usuario habilite el complemento y recibir la conexión.

## Comandos

```bash
dumpbin /exports payload.xll
swaks --to usuario@dominio --from soporte@dominio --attach payload.xll --body "Abre el complemento adjunto"
# La exportación relevante debe aparecer como xlAutoOpen
```

## Variantes

- Firmar el XLL con un certificado robado o de laboratorio.
- Usar un archivo `.xll` dentro de un ZIP para saltar filtros de extensión.
- Cambiar el icono y el nombre para que parezca una hoja de cálculo.

## Limitaciones

- Microsoft bloquea XLL no confiables por defecto desde 2023.
- Mark-of-the-Web y SmartScreen reducen la ejecución.
- La arquitectura del XLL debe coincidir con la de Excel.

## Mitigación

- Bloquear XLL desde Internet y ubicaciones no confiables.
- Aplicar ASR, WDAC/AppLocker y Mark-of-the-Web.
- Concienciar sobre complementos y archivos ejecutables disfrazados.

## Detección

- Excel cargando una DLL desde `Downloads`, `Temp` o un share.
- Eventos de creación de procesos hijos de `EXCEL.EXE`.
- Correos con adjuntos `.xll`, `.xla` o ZIP que los contienen.

## Referencias

- [0xdf — Axlle](https://0xdf.gitlab.io/2024/11/16/htb-axlle.html)
- [Microsoft — XLL add-ins](https://learn.microsoft.com/en-us/office/client-developer/excel/xll-add-ins)
- [MITRE T1204.002 — Malicious File](https://attack.mitre.org/techniques/T1204/002/)
