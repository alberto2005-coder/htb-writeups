---
title: WCF — inyección de comandos en un endpoint SOAP
tags: [windows, wcf, soap, dotnet, command-injection, privesc]
---

# WCF — inyección de comandos en un endpoint SOAP

[🇬🇧 English](wcf-soap-command-injection.en.md) | **Español**

## Concepto

Windows Communication Foundation (WCF) expone operaciones mediante SOAP. Si un método recibe una cadena y la concatena en `Process.Start`, `cmd.exe` o PowerShell, el endpoint se convierte en ejecución remota. Muchos servicios internos solo escuchan en `localhost`, así que primero hay que obtener una shell en el host.

## Cuándo aplica

- Hay un servicio WCF en un puerto poco habitual (por ejemplo, 8000).
- Se puede leer el contrato (`?wsdl`, `mex`) o descompilar el cliente .NET.
- El método acepta nombres de proceso, rutas o argumentos.

## Procedimiento

1. Localizar el endpoint y descargar el WSDL.
2. Enumerar operaciones y tipos con `svcutil` o `dotPeek`.
3. Construir un sobre SOAP con la `SOAPAction` correcta.
4. Inyectar un separador (`;`, `&`, `|`) y ejecutar un comando.

```bash
curl -s 'http://localhost:8000/MonitorService?wsdl' -o service.wsdl
svcutil service.wsdl
```

```text
POST /MonitorService/ HTTP/1.1
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://tempuri.org/IMonitoringService/KillProcess"

<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <KillProcess xmlns="http://tempuri.org/">
      <processName>x; powershell -e <BASE64>; #</processName>
    </KillProcess>
  </soap:Body>
</soap:Envelope>
```

## Variantes

- Inyectar en un argumento que se pasa a `cmd.exe /c`.
- Usar `ProcessStartInfo.FileName` con una ruta UNC para cargar un binario.
- Si el servicio corre como SYSTEM, la ejecución también es SYSTEM.

## Limitaciones

- El endpoint puede requerir autenticación Windows o un binding concreto.
- Algunos métodos validan el nombre contra una lista de procesos.
- El WSDL puede no estar publicado; hay que descompilar el cliente.

## Mitigación y detección

- No concatenar entrada en comandos; usar `ProcessStartInfo.ArgumentList`.
- Validar contra una lista de procesos permitidos.
- Ejecutar el servicio con una cuenta de mínimo privilegio.
- Auditar procesos hijos de `w3wp.exe` o del servicio WCF.

## Referencias

- <https://learn.microsoft.com/en-us/dotnet/framework/wcf/whats-wcf>
- <https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/security-overview>
- <https://owasp.org/www-community/attacks/Command_Injection>
